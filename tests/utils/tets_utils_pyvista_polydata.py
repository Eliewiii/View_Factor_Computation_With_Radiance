"""

"""
from pyvista import PolyData
import numpy as np

from src.radiance_comp_vf.utils import compute_polydata_area, compute_geometric_centroid, \
    compute_corners_from_existing_points

# Sample Polydata for testing
points = np.array([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]])
faces = np.array([[4, 0, 1, 2, 3]])
polydata_obj_1 = PolyData(points, faces)

points = np.array([[0., 0., 0.], [1., 0., 0.],[1.2, 0., 0.], [1., 0, 1.], [0., 0., 1.]])
faces = np.array([[5, 0, 1, 2, 3,4]])
polydata_obj_2 = PolyData(points, faces)

points = np.array([[-1., 0., 0.], [0., -1., 0.],[1., 0., 0.], [0., 1., 0.]])
faces = np.array([[4, 0, 1, 2, 3]])
polydata_obj_3 = PolyData(points, faces)


def test_compute_polydata_area():
    """
    Test the compute_polydata_area function.
    """
    area = compute_polydata_area(polydata_obj_1)
    assert area == 1.0


def test_compute_geometric_centroid():
    """
    Test the compute_geometric_centroid function.
    """
    centroid = compute_geometric_centroid(polydata_obj_1)
    assert np.allclose(centroid, [0.5, 0.5, 0.0])


def test_compute_corners_from_existing_points():
    """
    Test the compute_corners_from_existing_points function.
    """
    corners = compute_corners_from_existing_points(polydata_obj_1)
    print(corners)
    corners = compute_corners_from_existing_points(polydata_obj_2)
    print(corners)
    corners = compute_corners_from_existing_points(polydata_obj_3)
    print(corners)


def test_occurrences():
    """
    Test the compute_polydata_area function.
    """
    array = np.array([[1, 2, 3], [1, 4, 3], [2, 2, 3], [1, 2, 3], [1, 2, 3]])
    counts = np.sum(np.all(array == np.array([[1, 2, 3]]), axis=1))
    assert counts == 3


def test_intersection():
    """
    Test the compute_polydata_area function.
    """
    array1 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    array2 = np.array([[4, 5, 6], [10, 11, 12], [7, 8, 9], [13, 14, 15]])

    # Convert rows to sets of tuples for intersection
    array1_set = set(map(tuple, array1))
    array2_set = set(map(tuple, array2))

    # Find common rows
    common_rows = array1_set.intersection(array2_set)

    # Count of common rows
    count_common_rows = len(common_rows)
    print("Number of common vertices:", count_common_rows)

def test_call_vertex_and_faces():
    """
    Test the compute_polydata_area function.
    """
    points = np.array([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]])
    faces = np.array([[4, 0, 1, 2, 3],[4, 0, 1, 2, 3]])
    polydata_obj = PolyData(points, faces)
    print(polydata_obj.points)
    print(polydata_obj.faces)
