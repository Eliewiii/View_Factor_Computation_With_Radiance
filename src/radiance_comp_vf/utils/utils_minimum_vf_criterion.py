"""

"""
from math import sqrt, pi, atan, log

import numpy as np
import numpy.typing as npt


def does_surfaces_comply_with_minimum_vf_criterion(area_1: float, centroid_1: npt.NDArray[np.float64],
                                                   area_2: float, centroid_2: npt.NDArray[np.float64],
                                                   mvfc: float) -> bool:
    """
    """
    distance = np.linalg.norm(centroid_1 - centroid_2)
    vf = _compute_analytical_vf_coaxial_parallel_squares(area_1, area_2, distance)
    return vf >= mvfc


def _compute_analytical_vf_coaxial_parallel_squares(area_1: float, area_2: float, distance: float)-> float:
    """
        Maximal view factor between the 2 surface, in the optimal configuration described in the context paper
    """
    ## distance between the centroids
    d = distance
    if d == 0:  # avoid cases when surfaces are overlapping
        d = 0.01
    ## width of the optimal squares
    width_1 = sqrt(area_1)
    width_2 = sqrt(area_2)
    ## intermediary variable for the computation
    w_1 = width_1 / d  # "normalized width" of the surface 1
    w_2 = width_2 / d  # "normalized width" of the surface 2
    x = w_2 - w_1
    y = w_2 + w_1
    p = (w_1 ** 2 + w_2 ** 2 + 2) ** 2
    q = (x ** 2 + 2) * (y ** 2 + 2)
    u = sqrt(x ** 2 + 4)
    v = sqrt(y ** 2 + 4)
    s = u * (x * atan(x / u) - y * atan(y / u))
    t = v * (x * atan(x / v) - y * atan(y / v))

    return 1 / (pi * w_1 ** 2) * (log(p / q) + s - t)
