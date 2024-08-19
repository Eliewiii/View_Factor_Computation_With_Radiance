"""
Additional utility functions for working with PyVista PolyData objects.
"""
from pyvista import PolyData
import numpy as np


def compute_polydata_area(polydata_obj: PolyData) -> float:
    """
    Compute the area of the PolyData.
    :param polydata_obj: pv.PolyData, the PolyData object.
    :return: float, the area of the PolyData.
    """
    cell_sizes = polydata_obj.compute_cell_sizes()
    areas = cell_sizes['Area']
    return sum(areas)