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

# =========================================================
# GestureProcessor (stateful gesture + toggle logic)
# =========================================================

import time


class GestureProcessor:
    def __init__(self):
        self.gesture_candidate = None
        self.gesture_count = 0
        self.STABLE_FRAMES = 5

        self.stable_gesture = None

        self.toggle_start_time = None
        self.toggle_triggered = False

        self.enabled = True

    def update(self, gesture):
        new_key = None

        # -------------------------
        # NO INPUT
        # -------------------------
        if gesture is None:
            return {
                "stable": self.stable_gesture,
                "key": None,
                "enabled": self.enabled
            }

        # -------------------------
        # CANDIDATE TRACKING
        # -------------------------
        if self.gesture_candidate and gesture["key"] == self.gesture_candidate["key"]:
            self.gesture_count += 1
        else:
            self.gesture_candidate = gesture
            self.gesture_count = 1

        # -------------------------
        # STABLE UPDATE
        # -------------------------
        if self.gesture_count >= self.STABLE_FRAMES:
            self.stable_gesture = self.gesture_candidate

        stable = self.stable_gesture

        # -------------------------
        # TOGGLE LOGIC
        # -------------------------
        if stable is not None:
            key = stable["key"]

            if key == "Toggle":
                now = time.time()

                if self.toggle_start_time is None:
                    self.toggle_start_time = now
                    self.toggle_triggered = False

                elif not self.toggle_triggered:
                    if now - self.toggle_start_time >= 1.0:
                        self.enabled = not self.enabled
                        self.toggle_triggered = True

                new_key = None

            elif self.enabled and key != "Neutral":
                new_key = key

        # -------------------------
        # RESET TOGGLE STATE
        # -------------------------
        if stable is None or stable["key"] != "Toggle":
            self.toggle_start_time = None
            self.toggle_triggered = False

        return {
            "stable": stable,
            "key": new_key,
            "enabled": self.enabled
        }