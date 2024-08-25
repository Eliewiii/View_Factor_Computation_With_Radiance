"""
Function to contour a surface with holes in order to use it in Radiance simulations.
"""

import pyvista as pv
import numpy as np

from typing import List


def closest_point_index(vertex_list: List[np.ndarray], target_vertex: np.ndarray) -> int:
    """
    Find the index of the closest vertex to a target vertex in a list of vertices.
    :param vertex_list: List of vertices in 2 or 3 dimensions, it must be consistent with the target vertex.
    :param target_vertex: Target vertex in 2 or 3 dimensions.
    :return closest_index: Index of the closest vertex to the target vertex.
    """
    distances = np.linalg.norm(vertex_list - target_vertex, axis=1)
    return np.argmin(distances)


def contour_surface_with_hole(surface_boundary: List[List[int]], hole_vertex_list: List[List[int]]) -> List[List[int]]:
    """
    Contour a surface with a hole to exclude the hole from the surface, especially useful for Radiance. The hole is
        assumed to be a closed loop of vertices with the same orientation as the surface.
    :param surface_boundary: List of vertices of the surface in 2 or 3 dimensions, it must be consistent with the hole.
    :param hole_vertex_list: List of vertices of the hole in 2 or 3 dimensions, it must be consistent with the surface.
    :return new_surface_boundary: List of vertices of the contoured surface with the hole.
    """
    # Convert the input to numpy arrays
    surface_vertices = np.array(surface_boundary)
    hole_vertices = np.array(hole_vertex_list)
    """ Inverse the hole vertices to match as the hole should be "travelled" in the opposite direction not to create a
    surface with an intersection """
    hole_vertices = hole_vertices[::-1]
    # Find the closest points on the surface and hole
    surface_closest_index = closest_point_index(surface_vertices, hole_vertices[0])
    hole_closest_index = closest_point_index(hole_vertices, surface_vertices[surface_closest_index])
    # Split and merge the surface boundary
    new_surface_boundary = np.concatenate([
        surface_vertices[:surface_closest_index + 1],
        hole_vertices[hole_closest_index:],
        hole_vertices[:hole_closest_index+1],
        surface_vertices[surface_closest_index:]
    ])

    return new_surface_boundary


def contour_surface_with_multiple_holes(surface_boundary:List[List[int]],hole_list:List[List[List[int]]] ):
    """
    Contour a surface with multiple holes to exclude the holes from the surface, especially useful for Radiance.
    It assumes that the holes are closed loops of vertices with the same orientation as the surface and that the holes
        don't intersect.
    :param surface_boundary: List of vertices of the surface in 2 or 3 dimensions, it must be consistent with the holes.
    :param hole_list: List of lists of vertices of the holes in 2 or 3 dimensions, it must be consistent with the surface.
    :return new_surface_boundary: List of vertices of the contoured surface with the holes.
    """
    new_surface_boundary = surface_boundary
    for hole in hole_list:
        new_surface_boundary = contour_surface_with_hole(new_surface_boundary, hole)

    return new_surface_boundary
