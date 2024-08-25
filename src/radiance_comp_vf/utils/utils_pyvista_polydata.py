"""
Additional utility functions for working with PyVista PolyData objects.
"""
from pyvista import PolyData
import numpy as np

from shapely.geometry import Polygon

from typing import List, Tuple, Union


def polydata_from_vertices(vertices: np.ndarray) -> PolyData:
    """
    Create a PyVista PolyData object from vertices and faces.
    :param vertices: np.ndarray, the vertices of the PolyData object.
    :return: pv.PolyData, the PolyData object.
    """
    faces = np.array([[len(vertices)] + list(range(len(vertices)))])
    return PolyData(vertices, faces)


def polydata_to_shapely(polydata):
    # Extract points from the PolyData object
    points = polydata.points

    # Assuming there is only one face in the PolyData
    face = polydata.faces.reshape(-1, polydata.faces[0] + 1)[0,
           1:]  # Extracting the first face and ignoring the first number (which is the number of vertices in the face)

    # Extract the points corresponding to the face
    face_points = points[face]

    # Convert to a Shapely Polygon object
    polygon = Polygon(face_points)

    return polygon

def get_faces_list_of_vertices(polydata_obj: PolyData) -> List[List[float]]:
    """
    Get the list of vertices for each face of the PolyData object.
    :param polydata_obj: pv.PolyData, the PolyData object.
    :return list_of_vertices: List of vertices for each face.
    """
    # Extract points from the PolyData object
    points = polydata_obj.points
    # Extract the faces
    faces = polydata_obj.faces
    face_list=[]
    index = 0
    while index<len(faces):
        num_vertices = faces[index]
        face_list.append(faces[index+1:index+num_vertices+1])
        index += num_vertices+1
    list_of_vertices = [[points[pt_index] for pt_index in face] for face in face_list]

    return list_of_vertices


def compute_polydata_area(polydata_obj: PolyData) -> float:
    """
    Compute the area of the PolyData.
    :param polydata_obj: pv.PolyData, the PolyData object.
    :return: float, the area of the PolyData.
    """
    cell_sizes = polydata_obj.compute_cell_sizes()
    areas = cell_sizes['Area']
    return sum(areas)


def compute_geometric_centroid(polydata_obj: PolyData) -> np.ndarray:
    """
    Computes the geometric centroid of a planar surface represented as a PyVista PolyData object.
    The geometric centroid is the center of mass of the surface, considering it as a uniform material.
    :param polydata_obj: pv.PolyData, the PolyData object representing the planar surface.
    :return: np.ndarray, the geometric centroid of the surface.

    Notes:
        - The function assumes that the input surface is already a single planar polygon.
        - It automatically triangulates the surface if it's not already made of triangles.
    """
    # Triangulate the polygon to break it into triangles
    triangulated = polydata_obj.triangulate()
    # Get the points and the faces (which should now be triangles)
    points = triangulated.points
    # Reshape the faces array for easier processing
    faces = triangulated.faces.reshape(-1, 4)  # (Number of triangles, 4), where each row is [3, p0, p1, p2]
    """
    The faces array contains information about the triangles in the triangulated PolyData. 
    PyVista stores faces as a flat array. For example, for two triangles, the array might look like this:
        [3, 0, 1, 2, 3, 1, 2, 3]
    This represents:
        - First triangle with vertices at indices 0, 1, and 2.
        - Second triangle with vertices at indices 1, 2, and 3.
    Each face is preceded by the number '3' indicating it's a triangle (three vertices).

    By reshaping with .reshape(-1, 4):
        - The array is converted into a 2D array with 4 columns, where each row represents one triangle.
        - Example: 
            [[3, 0, 1, 2],  # First triangle
             [3, 1, 2, 3]]  # Second triangle
        - The first column (always '3') indicates it's a triangle, and the next three columns are vertex indices.
    """
    total_area = 0.0
    centroid = np.zeros(3)
    # Iterate over each triangle
    for face in faces:
        p0, p1, p2 = points[face[1]], points[face[2]], points[face[3]]
        # Calculate the area of the triangle
        area = 0.5 * np.linalg.norm(np.cross(p1 - p0, p2 - p0))
        # Calculate the centroid of the triangle
        triangle_centroid = (p0 + p1 + p2) / 3
        # Add to the weighted sum
        centroid += area * triangle_centroid
        total_area += area
    # Divide by the total area to get the centroid
    centroid /= total_area

    return centroid


def compute_corners_from_existing_points(polydata_obj: PolyData) -> np.ndarray:
    """
    Computes the corners of a planar surface using existing points of the PolyData object
    in the local coordinate system of the surface, then transforms these corners back to the
    original coordinate system. Handles cases where the normal vector is already aligned with
    the z-axis by using an alternative reference vector for rotation.
    :param polydata_obj: pv.PolyData, the PolyData object representing the planar surface.
    :return: np.ndarray, the corners of the surface in the original coordinate system.
    """

    # Compute normals using PyVista
    normal = polydata_obj.face_normals[0]  # Assuming the normal of the first point
    normal /= np.linalg.norm(normal)  # Normalize the normal vector

    # Define a reference vector for rotation
    x_axis = np.array([1, 0, 0])
    z_axis = np.array([0, 0, 1])
    if np.allclose(normal, z_axis) or np.allclose(normal, -z_axis):
        reference_vector = x_axis
    else:
        reference_vector = z_axis
    # Compute the rotation axis and angle
    basis_vector1 = reference_vector - np.dot(reference_vector, normal) * normal
    basis_vector1 = basis_vector1 / np.linalg.norm(basis_vector1)
    basis_vector2 = np.cross(normal, basis_vector1)
    transformation_matrix = create_transformation_matrix(normal, basis_vector1, basis_vector2)
    # Rotate the points to align the surface with the xy-plane in the local coordinate system
    points = polydata_obj.points
    local_points = points @ transformation_matrix
    print(local_points)
    # Get the minimum and maximum u and v values of the local points
    min_u = np.min(local_points[:, 0])
    max_u = np.max(local_points[:, 0])
    min_v = np.min(local_points[:, 1])
    max_v = np.max(local_points[:, 1])

    # Potential points for each extreme
    potential_u_min_points = local_points[np.isclose(local_points[:, 0], min_u)]
    potential_u_max_points = local_points[np.isclose(local_points[:, 0], max_u)]
    potential_v_min_points = local_points[np.isclose(local_points[:, 1], min_v)]
    potential_v_max_points = local_points[np.isclose(local_points[:, 1], max_v)]

    # Select unique points based on priority

    min_u_point = select_unique_point(potential_u_min_points, [],
                                      to_be_selected_points=[potential_v_min_points, potential_v_max_points,
                                                             potential_u_max_points])
    max_u_point = select_unique_point(potential_u_max_points, [min_u_point],
                                      to_be_selected_points=[potential_v_min_points, potential_v_max_points])
    max_v_point = select_unique_point(potential_v_max_points, [min_u_point, max_u_point],
                                      to_be_selected_points=[potential_u_max_points])
    min_v_point = select_unique_point(potential_v_min_points, [min_u_point, max_u_point, max_v_point],
                                      to_be_selected_points=[])

    # Corners are the combinations of these extreme points
    corners_local = np.array([
        max_u_point,  # Max u, corresponding v
        min_u_point,  # Min u, corresponding v
        max_v_point,  # Max v, corresponding u
        min_v_point  # Min v, corresponding u
    ])
    print(f"corners_local: {corners_local}")
    # Transform the corners back to the original coordinate system
    corners_original = corners_local @ np.linalg.inv(transformation_matrix)

    return corners_original


###
# Helper functions
###

# def compute_rotation_matrix(axis, angle):
#     """
#     Computes a rotation matrix given an axis and angle using Rodrigues' rotation formula.
#
#     Args:
#         axis (numpy.ndarray): The rotation axis.
#         angle (float): The rotation angle in radians.
#
#     Returns:
#         numpy.ndarray: The 3x3 rotation matrix.
#     """
#     axis = axis / np.linalg.norm(axis)  # Normalize the axis
#     cos_angle = np.cos(angle)
#     sin_angle = np.sin(angle)
#     ux, uy, uz = axis
#
#     return np.array([
#         [cos_angle + ux ** 2 * (1 - cos_angle), ux * uy * (1 - cos_angle) - uz * sin_angle,
#          ux * uz * (1 - cos_angle) + uy * sin_angle],
#         [uy * ux * (1 - cos_angle) + uz * sin_angle, cos_angle + uy ** 2 * (1 - cos_angle),
#          uy * uz * (1 - cos_angle) - ux * sin_angle],
#         [uz * ux * (1 - cos_angle) - uy * sin_angle, uz * uy * (1 - cos_angle) + ux * sin_angle,
#          cos_angle + uz ** 2 * (1 - cos_angle)]
#     ])


def create_transformation_matrix(normal, basis1, basis2):
    # Ensure the normal is pointing in the direction you want (e.g., z-direction)
    normal = normal / np.linalg.norm(normal)

    # Create a matrix with basis vectors as columns
    transformation_matrix = np.column_stack([basis1, basis2, normal])

    return transformation_matrix


def select_unique_point(potential_points: List[np.array], selected_points: np.array,
                        to_be_selected_points: List[np.array]) -> np.array:
    """
    Selects a unique point (as far as possible), from the potential points based on the selected points
        and the points to be selected.
    :param potential_points: List[np.array], the list of potential points.
    :param selected_points: List[np.array], the list of already selected points.
    :param to_be_selected_points: List[np.array], the list of points to be selected.
    :return: np.array, the selected point, unique if possible.
    """
    unique_point = potential_points[0]
    occurrences, min_option_left = get_occurrences(to_be_selected_points, selected_points, unique_point)
    for point in potential_points:
        if not any(np.allclose(point, sel_point) for sel_point in selected_points):
            local_occurrences, local_min_option_left = get_occurrences(to_be_selected_points, selected_points,
                                                                       point)
            if local_occurrences <= occurrences and local_min_option_left >= min_option_left:
                unique_point = point  # The priority is to select a point not already selected.
                occurrences, min_option_left = local_occurrences, local_min_option_left
                if occurrences == 0:
                    return point
    return unique_point  # Fallback if no unique point found


def get_occurrences(to_be_selected_points: List[np.array], selected_points_array: np.array,
                    point: np.array) -> (int, int):
    """
    Get the number of occurrences of a point in an array.
    :param to_be_selected_points:
    :param selected_points_array:
    :param point: np.array, the point to count.
    :return: int, the number of occurrences and the minimum number of options left of a surface with
        the occurence.
    """
    if len(to_be_selected_points) == 0:
        return 0, 0
    occurrence, min_option_left = 0, max([len(array) for array in to_be_selected_points])
    for array in to_be_selected_points:
        if np.sum(np.all(array == point, axis=1)) > 0:
            occurrence += 1
            if len(array) - nb_intersection(array, selected_points_array) < min_option_left:
                min_option_left = len(array) - nb_intersection(array, selected_points_array)
    return occurrence, min_option_left


def nb_intersection(array1: np.array, array2: np.array) -> int:
    """
    Compute the number of intersections between two arrays.
    :param array1: np.array, the first array.
    :param array2: np.array, the second array.
    :return: int, the number of intersections.
    """
    # Convert rows to sets of tuples for intersection
    array1_set = set(map(tuple, array1))
    array2_set = set(map(tuple, array2))

    # Find common rows
    common_rows = array1_set.intersection(array2_set)

    # Count of common rows
    count_common_rows = len(common_rows)
    return count_common_rows
