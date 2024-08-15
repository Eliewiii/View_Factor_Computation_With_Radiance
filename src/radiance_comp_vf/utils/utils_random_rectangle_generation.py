"""

"""
import sys

import random

import numpy as np
import pyvista as pv
from typing import List


def generate_random_rectangles(min_size: float = 0.0001, max_size: float = 100.,
                               max_distance_factor: float = 100., parallel_coaxial_squares: bool = False,
                               nb_random_rectangles: int = 1) -> [pv.Rectangle, List[pv.Rectangle]]:
    """
    Generate a reference rectangle and a random rectangle that faces the reference rectangle.
    :param min_size: The minimum size of an edge of the rectangles.
    :param max_size: The maximum size of an edge of the rectangles.
    :param max_distance_factor: The maximum distance factor between the reference rectangle and the random rectangle.
    :param parallel_coaxial_squares: If True, the width of the rectangle is set to 1. to make a normalized square.
    :param nb_random_rectangles: The number of random rectangles to generate.
    :return: The reference rectangle and the list of random rectangle.
    """

    def generate_ref_rectangle_in_xy_plane(parallel_coaxial_squares: bool = False):
        """
        Generate a rectangle in the (x, y) plane.
        :param parallel_coaxial_squares: If True, the width of the rectangle is set to 1. to make a normalized square.
        """
        if parallel_coaxial_squares:
            width = 1.
        else:
            width = random.uniform(min_size, max_size)
        pointa = [1., 0., 0.]
        pointb = [1., width, 0.]
        pointc = [0., width, 0.]
        pointd = [0., 0., 0.]
        return pv.Rectangle([pointa, pointb, pointc])

    def generate_random_rectangle(ref_rectangle: pv.Rectangle,
                                  parallel_coaxial_squares: bool = False) -> pv.Rectangle:
        """
        Generate a random rectangle that faces the reference rectangle.
        :param ref_rectangle: The reference rectangle.
        :param parallel_coaxial_squares: If True, the width of the rectangle is set to 1. to make a normalized square.
        """
        if not parallel_coaxial_squares:
            # Select a random vertex for the centroid of the new rectangle
            ref_rectangle_centroid = np.array(ref_rectangle.center)
            rectangle_centroid = random_point_with_maximum_distance_from_point(point=ref_rectangle_centroid,
                                                                               max_distance=max_distance,
                                                                               ensure_z_posive=True)
            # Select a random normal unit vector for the new rectangle
            ref_rectangle_normal_unit_vector = rectangle_normal(ref_rectangle)
            rectangle_normal_unit_vector = random_face_normal_vector_facing_face(
                vertex_ref=ref_rectangle_centroid, normal_ref=ref_rectangle_normal_unit_vector,
                vertex_new=rectangle_centroid, normalize=True)
            # Select random orthogonal unit vectors for the new rectangle
            (ortho_vec1, ortho_vec2) = random_orthonormal_vectors(normal_vec=rectangle_normal_unit_vector,
                                                                  normalize=True)
            # Size of the random rectangle
            random_width = random.uniform(min_size, max_size)
            random_length = random.uniform(min_size, max_size)
        else:
            # Select a random vertex for the centroid of the new rectangle
            ref_rectangle_centroid = np.array(ref_rectangle.center)
            rectangle_centroid = random_point_with_maximum_distance_from_point(point=ref_rectangle_centroid,
                                                                               max_distance=max_distance,
                                                                               ensure_z_posive=True,
                                                                               enforce_z_direction=True)
            # Select a random normal unit vector for the new rectangle
            ref_rectangle_normal_unit_vector = rectangle_normal(ref_rectangle)
            rectangle_normal_unit_vector = np.array([0., 0., -1.])
            # Select random orthogonal unit vectors for the new rectangle
            (ortho_vec1, ortho_vec2) = random_orthonormal_vectors(normal_vec=rectangle_normal_unit_vector,
                                                                  normalize=True, enforce_y_x=True)
            # Size of the random rectangle
            random_width = random.uniform(min_size, max_size)
            random_length = random_width

        # Generate the random rectangle ensuring the orientation of the rectangle according to the normal vector
        point_a = rectangle_centroid + 0.5 * random_width * ortho_vec1 - 0.5 * random_length * ortho_vec2
        point_b = point_a + random_length * ortho_vec2
        point_c = point_b - random_width * ortho_vec1
        point_d = point_c - random_length * ortho_vec2
        # Check that the rectangle is properly oriented
        is_rectangle_oriented_to_normal(normal_vec=rectangle_normal_unit_vector, point_a=point_a,
                                        point_b=point_b,
                                        point_c=point_c)

        return pv.Rectangle([point_a, point_b, point_c])

    # Set the maximum distance with an arbitrary factor
    max_distance = max_distance_factor * max_size
    # Generate the reference rectangle
    ref_rectangle = generate_ref_rectangle_in_xy_plane(parallel_coaxial_squares=parallel_coaxial_squares)
    # Generate the random rectangle
    random_rectangle_list = [
        generate_random_rectangle(ref_rectangle, parallel_coaxial_squares=parallel_coaxial_squares) for
        i in range(nb_random_rectangles)]

    return ref_rectangle, random_rectangle_list


def random_face_normal_vector_facing_face(vertex_ref: np.ndarray, normal_ref: np.ndarray,
                                          vertex_new: np.ndarray, normalize: bool = False):
    """
    Generate a random face normal vector facing a reference face.
    :param vertex_ref: The reference face vertex.
    :param normal_ref: The reference face normal vector.
    :param vertex_new: The new face vertex.
    :param normalize: Normalize the random face normal vector.
    :return: The random face normal vector.
    """
    random_normal_unit_vector = random_nonzero_vector(normalize=normalize)
    # Check if the faces are facing each other
    if not are_faces_facing(vertex_ref, normal_ref, vertex_new, random_normal_unit_vector):
        random_normal_unit_vector = - random_normal_unit_vector
        if not are_faces_facing(vertex_ref, normal_ref, vertex_new, random_normal_unit_vector):
            raise ValueError("Could not generate a random face normal vector facing the reference face")

    return random_normal_unit_vector


def random_point_with_maximum_distance_from_point(point: np.ndarray, max_distance: float,
                                                  ensure_z_posive: bool = True,
                                                  enforce_z_direction: bool = False) -> np.ndarray:
    """
    Generate a random point with a maximum distance from a given point.
    :param point: The given point.
    :param max_distance: The maximum distance.
    :param ensure_z_posive: Ensure the z coordinate of the random point is positive.
    :param enforce_z_direction: Ensure direction of the "translation" is z.
    :return: The random point.
    """
    # normalize the random vector
    random_distance = max_distance * random.uniform(sys.float_info.epsilon, 1)
    # make a random vector
    if enforce_z_direction:
        random_unit_vector = np.array([0, 0, 1])
    else:
        random_unit_vector = random_nonzero_vector(ensure_z_posive=ensure_z_posive, normalize=True)

    return point + random_distance * random_unit_vector


def random_orthonormal_vectors(normal_vec: np.ndarray, normalize: bool = False, enforce_y_x: bool = False) -> \
        tuple[
            np.ndarray, np.ndarray]:
    """
    Generate two random orthonormal vectors.
    :param normal_vec: The normal vector.
    :param normalize: Normalize the orthogonal vectors.
    :param enforce_y_x: Ensure the orthogonal vectors are x and y
    :return: Two orthogonal vectors.
    """
    if enforce_y_x:
        ortho_vec2 = np.array([1., 0., 0.])
        ortho_vec1 = np.array([0., 1., 0.])
        return ortho_vec1, ortho_vec2
    # Generate a random vector
    rand_vec = non_parallel_random_nonzero_vector(normal_vec=normal_vec)
    # Project rand_vec onto normal_vec to get a component parallel to normal_vec
    parallel_component = np.dot(rand_vec, normal_vec) * normal_vec
    # Subtract the parallel component from rand_vec to get a vector perpendicular to normal_vec
    perpendicular_vec = rand_vec - parallel_component
    # Normalize the perpendicular vector to get the first orthogonal vector
    ortho_vec1 = normalize_vector(perpendicular_vec)
    # Calculate the second orthonormal vector, ensuring the orientation of the new coordinate system
    ortho_vec2 = np.cross(normal_vec, ortho_vec1)
    # Normalize the second orthogonal vector
    ortho_vec2 /= np.linalg.norm(ortho_vec2)

    if normalize:
        ortho_vec1 = normalize_vector(ortho_vec1)
        ortho_vec2 = normalize_vector(ortho_vec2)

    return ortho_vec1, ortho_vec2


def are_faces_facing(centroid_1: np.ndarray, normal_1: np.ndarray, centroid_2: np.ndarray,
                     normal_2: np.ndarray):
    """
    Visibility check between 2 faces
    :param centroid_1: centroid of the first face
    :param normal_1: normal vector of the first face
    :param centroid_2: centroid of the second face
    :param normal_2: normal vector of the second face
    :return: True if the faces are facing each other, False otherwise
    """
    # vectors from centroid_2 to centroid_1
    vector_21 = centroid_1 - centroid_2
    # dot product
    dot_product_sup = normal_2.dot(vector_21)
    dot_product_inf = normal_1.dot(vector_21)
    # visibility/facing criteria  (same as PyviewFactor)
    if dot_product_sup > 0 > dot_product_inf:
        return True
    else:
        return False


def is_rectangle_oriented_to_normal(normal_vec: np.ndarray, point_a: np.ndarray, point_b: np.ndarray,
                                    point_c: np.ndarray) -> bool:
    """
    Check if a rectangle is oriented according to a normal vector.
    :param normal_vec: The normal vector.
    :param point_a: The first point of the rectangle.
    :param point_b: The second point of the rectangle.
    :param point_c: The third point of the rectangle.
    """
    # Calculate the normal vector of the rectangle
    rectangle_normal = np.cross(point_b - point_a, point_c - point_a)
    # Check if the normal vector of the rectangle is parallel to the given normal vector
    if np.linalg.norm(np.cross(rectangle_normal, normal_vec)) < 1e-6:
        return True
    raise ValueError("The rectangle is not oriented according to the normal vector")


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalize a vector
    :param vector: vector to normalize
    :return: normalized vector
    """
    # Ensure the norm is not zero
    if np.linalg.norm(vector) < 1e-6:
        raise ValueError("Cannot normalize a vector with zero norm")
    return vector / np.linalg.norm(vector)


def non_parallel_random_nonzero_vector(normal_vec: np.ndarray) -> np.ndarray:
    """ Generate a random nonzero 3D vector that is not parallel to a given normal vector. """
    for i in range(100):
        rand_vec = random_nonzero_vector()
        # Check if the cross product is not close to zero
        if np.linalg.norm(np.cross(rand_vec, normal_vec)) > 1e-6:
            return rand_vec
    raise ValueError(
        "Could not generate a nonzero vector that is not parallel to the given vector after 100 attempts")


def rectangle_normal(rectangle: pv.Rectangle, normalize: bool = False) -> np.ndarray:
    """
    Calculate the normal vector of a rectangle defined by its vertices.
    :param rectangle: pv.Rectangle object representing the rectangle.
    :param normalize: Normalize the normal vector.
    :return: Normal vector of the rectangle.
    """
    points = np.array(rectangle.points)
    edge_vec1 = points[1] - points[0]
    edge_vec2 = points[2] - points[1]
    normal_vec = np.cross(edge_vec1, edge_vec2)
    if normalize:
        return normalize_vector(normal_vec)
    return normal_vec


def random_nonzero_vector(ensure_z_posive: bool = False, ensure_z_negative=False,
                          normalize: bool = False) -> np.ndarray:
    """Generate a random nonzero 3D vector."""
    for i in range(100):
        rand_vec = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
        if ensure_z_posive:
            rand_vec[2] = abs(rand_vec[2])
        if ensure_z_negative:
            rand_vec[2] = -abs(rand_vec[2])
        if np.linalg.norm(rand_vec) > 1e-6:  # Check if norm is not too close to zero
            if normalize:
                return normalize_vector(rand_vec)
            return rand_vec
    raise ValueError("Could not generate a nonzero vector after 100 attempts")
