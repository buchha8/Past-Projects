import numpy as np


def initialize_order(blendshape_dict):
    """
    Returns a frozen canonical order (alphabetical).
    """

    if blendshape_dict is None:
        raise ValueError("Cannot initialize order from None")

    return sorted(blendshape_dict.keys())


def dict_to_vector(blendshape_dict, order):
    """
    dict[str, float] -> np.ndarray
    """

    if blendshape_dict is None:
        return None

    return np.array(
        [float(blendshape_dict.get(k, 0.0)) for k in order],
        dtype=np.float32
    )


def vector_to_dict(vector, order):
    """
    np.ndarray -> dict[str, float]
    """

    if vector is None:
        return None

    return {
        k: float(v)
        for k, v in zip(order, vector)
    }

def cosine_similarity(a, b):
    if a is None or b is None:
        return -1.0

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return -1.0

    return float(np.dot(a, b) / (norm_a * norm_b))

def get_stored_gesture_vectors(config, order):
    keybinds = config.get("keybinds", [])

    result = []

    for kb in keybinds:
        gesture = kb.get("gesture")

        if not gesture:
            continue

        vec = dict_to_vector(gesture["blendshapes"], order)

        result.append({
            "key": kb["key"],
            "name": gesture["name"],
            "vector": vec,
            "sensitivity": kb["sensitivity"]
        })

    return result

def weighted_cosine_similarity(a, b, w):
    # proper weighted cosine (NOT elementwise scaling)
    a_w = a * w
    b_w = b * w

    dot = np.dot(a_w, b_w)
    norm_a = np.linalg.norm(a_w)
    norm_b = np.linalg.norm(b_w)

    if norm_a == 0 or norm_b == 0:
        return -1.0

    return float(dot / (norm_a * norm_b))


def compute_gesture(current_blendshapes, config, order):
    if current_blendshapes is None:
        return None

    current_vec = dict_to_vector(current_blendshapes, order)
    stored = get_stored_gesture_vectors(config, order)

    if not stored:
        return None

    # -------------------------
    # GET NEUTRAL VECTOR
    # -------------------------
    neutral_vec = None
    for g in stored:
        if g["key"] == "Neutral":
            neutral_vec = g["vector"]
            break

    if neutral_vec is None:
        return None

    # -------------------------
    # NORMALIZATION
    # -------------------------
    current_vec = current_vec - neutral_vec

    normalized = []
    for g in stored:
        normalized.append({
            "key": g["key"],
            "name": g["name"],
            "vector": g["vector"] - neutral_vec,
            "sensitivity": g["sensitivity"]
        })

    # -------------------------
    # SOFT AUTO-WEIGHTS
    # -------------------------
    all_vectors = np.stack([g["vector"] for g in normalized])

    variance = np.var(all_vectors, axis=0)

    # soften influence (IMPORTANT FIX)
    weights = 1.0 / np.sqrt(variance + 1e-6)

    # normalize weights to prevent scaling explosion
    weights = weights / (np.mean(weights) + 1e-6)

    # clamp weights to prevent instability
    weights = np.clip(weights, 0.5, 2.0)

    # -------------------------
    # CLASSIFICATION
    # -------------------------
    best = None
    best_score = -1.0
    second_best_score = -1.0

    for g in normalized:
        score = weighted_cosine_similarity(
            current_vec,
            g["vector"],
            weights
        )

        score *= g["sensitivity"]

        if score > best_score:
            second_best_score = best_score
            best_score = score
            best = g
        elif score > second_best_score:
            second_best_score = score

    # -------------------------
    # THRESHOLDS
    # -------------------------
    COSINE_THRESHOLD = 0.4
    if best_score < COSINE_THRESHOLD:
        return None

    MARGIN_THRESHOLD = 0.2
    if best_score - second_best_score < MARGIN_THRESHOLD:
        return None

    return best