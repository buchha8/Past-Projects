import numpy as np


def initialize_order(blendshape_dict):
    if blendshape_dict is None:
        raise ValueError("Cannot initialize order from None")

    return sorted(blendshape_dict.keys())


def dict_to_vector(blendshape_dict, order):
    if blendshape_dict is None:
        return None

    return np.array(
        [float(blendshape_dict.get(k, 0.0)) for k in order],
        dtype=np.float32
    )


def vector_to_dict(vector, order):
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


def compute_gesture(current_blendshapes, config, order):
    # -------------------------
    # HARD FAILURE ONLY
    # -------------------------
    if current_blendshapes is None:
        return None

    current_vec = dict_to_vector(current_blendshapes, order)

    stored = get_stored_gesture_vectors(config, order)
    if not stored:
        return None

    # -------------------------
    # FIND NEUTRAL
    # -------------------------
    neutral_vec = None
    for g in stored:
        if g["key"] == "Neutral":
            neutral_vec = g["vector"]
            break

    if neutral_vec is None:
        return None

    # -------------------------
    # NEUTRAL RELATIVE SPACE
    # -------------------------
    current_vec = current_vec - neutral_vec

    best = None
    best_score = -1.0
    second_best_score = -1.0

    for g in stored:
        g_vec = g["vector"] - neutral_vec

        score = cosine_similarity(current_vec, g_vec)
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
    MARGIN_THRESHOLD = 0.2

    # If confidence is low → Neutral
    if best_score < COSINE_THRESHOLD:
        return {
            "key": "Neutral",
            "name": "Neutral"
        }

    # If ambiguous → Neutral
    if (best_score - second_best_score) < MARGIN_THRESHOLD:
        return {
            "key": "Neutral",
            "name": "Neutral"
        }

    return best