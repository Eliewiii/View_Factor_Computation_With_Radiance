"""

"""
from pyvista import PolyData
import numpy as np

from src.radiance_comp_vf.utils import compute_polydata_area

# Sample Polydata for testing
points = np.array([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]])
faces = np.array([[4,0,1,2,3]])
polydata_obj_1 = PolyData(points, faces)

def test_compute_polydata_area():
    """
    Test the compute_polydata_area function.
    """
    area = compute_polydata_area(polydata_obj_1)
    assert area == 1.0
