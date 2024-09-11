"""
Utils functions for the visibility analysis of planar surfaces.
"""

from typing import List

from geoplus import are_planar_surface_vertices_seeing_each_other


from ..decorators import check_for_list_of_inputs


@check_for_list_of_inputs
def are_planar_surfaces_seeing_each_other(vertex_surface_1: List[List[float]], vertex_surface_2: List[List[float]],
                                         normal_1: List[float], normal_2: List[float]):
    """

    This function checks if two planar surfaces are seeing each other.
    The decorator @check_for_list_of_inputs force the function to accept lists of vertex instead of single vertices
    The original function accepts single vertices.
    It facilitates batch processing to check multiple vertices couples of the surfaces.

    :param vertex_surface_1: A vertex of the first surface
    :param vertex_surface_2: A vertex of the second surface
    :param normal_1: Normal vector of the first surface
    :param normal_2: Normal vector of the second surface
    :return: True if the two surfaces are seeing each other, False otherwise.
    """
    return are_planar_surface_vertices_seeing_each_other(vertex_surface_1=vertex_surface_1,
                                                            vertex_surface_2=vertex_surface_2,
                                                            normal_1=normal_1,
                                                            normal_2=normal_2)