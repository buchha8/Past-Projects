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