import numpy as np
import pyvista as pv

from src.radiance_comp_vf.radiative_surface import RadiativeSurface

from src.radiance_comp_vf.utils import (contour_surface_with_hole, contour_surface_with_multiple_holes, \
    closest_point_index, polydata_from_vertices, compute_polydata_area, polydata_to_shapely,compute_geometric_centroid,
                                        compute_area_and_centroid_of_polydata)


def test_centroid_of_surface():
    """

    :return:
    """
    # Example usage:
    surface = [
        [0, 0, 0],
        [10, 0, 0],
        [10, 10, 10],
        [0, 10, 10]
    ]
    polydata_obj = polydata_from_vertices(surface)

    area,centroid =compute_area_and_centroid_of_polydata(polydata_obj)
    print("")
    print(area,centroid)

def test_centroid_of_surface_with_hole():
    """

    :return:
    """
    # Example usage:
    surface = [
        [0, 0, 0],
        [10, 0, 0],
        [10, 10, 10],
        [0, 10, 10]
    ]
    hole = [
        [3, 3, 3],
        [6, 3, 3],
        [6, 6, 6],
        [3, 6, 6]
    ]
    # Get the contoured surface with multiple holes
    contoured_surface = contour_surface_with_hole(surface, hole)
    polydata_obj = polydata_from_vertices(contoured_surface)

    area, centroid = compute_area_and_centroid_of_polydata(polydata_obj)
    print("")
    print(area, centroid)