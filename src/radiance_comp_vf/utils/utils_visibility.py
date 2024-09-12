"""
Utils functions for the visibility analysis of planar surfaces.
"""

import pyvista as pv
import numpy as np

from typing import List
import numpy.typing as npt

from geoplus import are_planar_surface_vertices_facing_each_other, is_ray_intersecting_context

from ..decorators import check_for_list_of_inputs

RAY_OFFSET = 0.05  # offset to avoid considering the sender and receiver in the raytracing obstruction detection


@check_for_list_of_inputs(check_for_true=True)
def are_planar_surfaces_facing_each_other(vertex_surface_1: npt.NDArray[np.float64],
                                          vertex_surface_2: npt.NDArray[np.float64],
                                          normal_1: npt.NDArray[np.float64], normal_2: npt.NDArray[np.float64]):
    """
    This function checks if two planar surfaces are seeing each other.
    Note:
        The decorator @check_for_list_of_inputs force the function to accept lists of vertex instead of single vertices.
        It returns True as soon as one couple of vertices of the two surfaces are seeing each other, False otherwise.
        The original function accepts single vertices.
        It facilitates batch processing to check multiple vertices couples of the surfaces.

    :param vertex_surface_1: A vertex of the first surface
    :param vertex_surface_2: A vertex of the second surface
    :param normal_1: Normal vector of the first surface
    :param normal_2: Normal vector of the second surface
    :return: True if the two surfaces are seeing each other, False otherwise.
    """
    return are_planar_surface_vertices_facing_each_other(vertex_surface_1=vertex_surface_1,
                                                         vertex_surface_2=vertex_surface_2,
                                                         normal_1=normal_1,
                                                         normal_2=normal_2)


@check_for_list_of_inputs(check_for_true=False)
def is_ray_between_surfaces_intersect_with_context(start_point: npt.NDArray[np.float64],
                                                   end_point: npt.NDArray[np.float64],
                                                   context_polydata_mesh: pv.PolyData,
                                                   offset: float = RAY_OFFSET) -> bool:
    """
    Check if a ray intersects a context mesh.

    :param start_point: numpy array vertex of the start point of the ray
    :param end_point: numpy array vertex of the end point of the ray
    :param context_polydata_mesh: PyVista PolyData object of the context mesh
    :param offset: float, offset to avoid considering the sender and receiver in the raytracing obstruction detection
    :return:
    """
    return is_ray_intersecting_context(start_point=start_point, end_point=end_point,
                                       context_polydata_mesh=context_polydata_mesh, offset=offset)

# =========================================================
# Private Helper Functions
# =========================================================
