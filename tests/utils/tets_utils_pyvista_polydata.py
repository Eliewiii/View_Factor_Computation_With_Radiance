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

points = np.array([[0., 0., 0.], [1., 0., 0.], [1., 0, 1.], [0., 0., 1.]])
faces = np.array([[4, 0, 1, 2, 3]])
polydata_obj_2 = PolyData(points, faces)

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
    print (corners)
    corners = compute_corners_from_existing_points(polydata_obj_2)
    print(corners)


def test_occurrences():
    """
    Test the compute_polydata_area function.
    """
    array = np.array([[1, 2, 3], [1, 4, 3], [2, 2, 3], [1, 2, 3],[1, 2, 3]])
    counts = np.sum(np.all(array == np.array([[1,2,3]]), axis=1))
    assert counts == 3