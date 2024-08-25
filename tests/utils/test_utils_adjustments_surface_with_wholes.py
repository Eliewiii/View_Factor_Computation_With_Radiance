"""

"""

import numpy as np
import pyvista as pv

from src.radiance_comp_vf.radiative_surface import RadiativeSurface

from src.radiance_comp_vf.utils import contour_surface_with_hole, contour_surface_with_multiple_holes, \
    closest_point_index, polydata_from_vertices, compute_polydata_area, polydata_to_shapely,compute_geometric_centroid


def test_closest_point_index():
    """
    Test the object_method_wrapper function.
    """
    # Example usage:
    points = np.array([
        [0, 0],
        [10, 0],
        [10, 10],
        [0, 10]
    ])
    # Target point 1
    target_point = np.array([7, 7])
    closest_index = closest_point_index(points, target_point)
    assert closest_index == 2
    # Target point 2
    target_point = np.array([3, 3])
    closest_index = closest_point_index(points, target_point)
    assert closest_index == 0


def test_contour_surface_with_hole():
    """
    Test the object_method_wrapper function.
    """
    # Example usage:
    surface = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)]
    hole = [(4, 4, 0), (6, 4, 0), (6, 6, 0), (4, 6, 0)]  # First hole

    # Get the contoured surface with multiple holes
    contoured_surface = contour_surface_with_hole(surface, hole)
    # Convert to a PyVista PolyData object for visualization
    face = np.array([[len(contoured_surface)] + list(range(len(contoured_surface)))])
    surface_polydata = pv.PolyData(contoured_surface, face)
    print(contoured_surface)


def test_contour_surface_with_multiple_hole():
    """
    Test the object_method_wrapper function.
    """
    # Example usage:
    surface = [(0, 0), (10, 0), (10, 10), (0, 10)]
    holes = [
        [(4, 4), (6, 4), (6, 6), (4, 6)],  # First hole
        [(7, 7), (8, 7), (8, 8), (7, 8)]  # Second hole
    ]

    # Get the contoured surface with multiple holes
    contoured_surface = contour_surface_with_multiple_holes(surface, holes)

    # Convert to a PyVista PolyData object for visualization
    surface_polydata = pv.PolyData(contoured_surface)

    # Visualize the contoured surface with holes
    plotter = pv.Plotter()
    plotter.add_mesh(surface_polydata, color='cyan', line_width=2)

    # Visualize each hole
    for hole in holes:
        plotter.add_mesh(pv.PolyData(np.array(hole)), color='red', point_size=10)

    plotter.show()


def test_area_of_surface_with_hole():
    """

    :return:
    """
    # Example usage:
    surface = [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)]
    hole = [(4, 4, 0), (6, 4, 0), (6, 6, 0), (4, 6, 0)]  # First hole

    # Get the contoured surface with multiple holes
    contoured_surface = contour_surface_with_hole(surface, hole)
    # Convert to a PyVista PolyData object for visualization
    print(contoured_surface)

    polydata_obj = polydata_from_vertices(contoured_surface)

    area_pv = compute_polydata_area(polydata_obj)
    polygon = polydata_to_shapely(polydata_obj)
    area_shapely = polygon.area

    print(area_pv, area_shapely)

    # surface_polydata= polydata_from_vertices(surface)
    # hole_polydata= polydata_from_vertices(hole)
    #
    #
    # assert area == compute_polydata_area(surface_polydata) - compute_polydata_area(hole_polydata)
    #
    #
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
        [4, 4, 4],
        [6, 4, 4],
        [6,6, 6],
        [4, 6, 6]
    ]

    # Get the contoured surface with multiple holes
    contoured_surface = contour_surface_with_hole(surface, hole)
    # Convert to a PyVista PolyData object for visualization
    print(contoured_surface)

    polydata_obj = polydata_from_vertices(contoured_surface)

    area_pv = compute_polydata_area(polydata_obj)
    polygon = polydata_to_shapely(polydata_obj)
    area_shapely = polygon.area

    print(area_pv, area_shapely)

    # surface_polydata= polydata_from_vertices(surface)
    # hole_polydata= polydata_from_vertices(hole)
    #
    #
    # assert area == compute_polydata_area(surface_polydata) - compute_polydata_area(hole_polydata)
    #
    #



