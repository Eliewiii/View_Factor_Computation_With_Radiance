"""
Utils functions for the visibility analysis of planar surfaces.
"""

from typing import List

import pyvista as pv

from geoplus import are_planar_surface_vertices_facing_each_other


from ..decorators import check_for_list_of_inputs


@check_for_list_of_inputs
def are_planar_surfaces_facing_each_other(vertex_surface_1: List[List[float]], vertex_surface_2: List[List[float]],
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
    return are_planar_surface_vertices_facing_each_other(vertex_surface_1=vertex_surface_1,
                                                            vertex_surface_2=vertex_surface_2,
                                                            normal_1=normal_1,
                                                            normal_2=normal_2)


def is_ray_intersection_context(start_point:List[float], end_point:List[float], context_polydata_mesh:pv.PolyData):
    """
    Check if a ray intersects a context mesh.
    Important note: The start and end points of the ray should not be on one of the faces of the context mesh. It is
        import to correct the ray before using this function, by using a small offsets from the original surfaces
        (if there is any) to avoid the intersection with the sender and receiver faces.
    :param start_point: Vertex of the start point of the ray
    :param end_point:
    :param context_polydata_mesh:
    :return:
    """



def correct_rays(ray_list, face_receiver, exclude_surface_from_ray=True, lower_ray_z_axis=True):
    """ Correct the rays to avoid considering the sender and receiver in the raytracing obstruction detection
        :param ray_list: list of rays
        :param face_receiver: Honeybee Face or Ladybug Face3D
        :param exclude_surface_from_ray: bool, True if the surfaces should be excluded from the ray
        :param lower_ray_z_axis: bool, True if the z axis of the ray should be lowered
        :return: corrected ray list
        """
    number_of_rays = len(ray_list)

    if exclude_surface_from_ray:
        for i in range(number_of_rays):
            new_start_point, new_end_point = excluding_surfaces_from_ray(start_point=ray_list[i][0],
                                                                         end_point=ray_list[i][1])
            new_start_point[2], new_end_point[2] = ray_list[i][0][2], ray_list[i][1][
                2]  # correct the z coordinate. it does not influence here
            ray_list[i] = (new_start_point, new_end_point)
            if is_vector3d_vertical(face_receiver.normal):
                ray_list[i] = (ray_list[i][0] + np.array([0, 0, 0.1]), ray_list[i][1] + np.array([0, 0, 0.1]))
    if lower_ray_z_axis:  # todo @Elie: DO SOMETHING ABOUT THIS
        for i in range(number_of_rays):
            if not is_vector3d_vertical(face_receiver.normal):
                ray_list[i] = (ray_list[i][0], ray_list[i][1] - np.array([0, 0, 0.1]))

def ray_list_from_emitter_to_receiver(face_emitter, face_receiver, exclude_surface_from_ray=True,
                                      lower_ray_z_axis=True, number_of_rays=3):
    """
        Args:
        todo @Elie
        Output:
            ray list, with ray tuple (start, stop)
    """
    # todo @Elie: check if it works
    # Check the type of the input, could be either a Ladybug Face3D or a Honeybee Face for more flexibility
    if isinstance(face_emitter, Face3D):
        emitter_face3d = face_emitter
    elif isinstance(face_emitter, Face):
        emitter_face3d = face_emitter.geometry
    else:
        raise TypeError("face_emitter should be a Ladybug Face3D or a Honeybee Face object")

    if isinstance(face_receiver, Face3D):
        receiver_face3d = face_receiver
    elif isinstance(face_receiver, Face):
        receiver_face3d = face_receiver.geometry
    else:
        raise TypeError("face_receiver should be a Ladybug Face3D or a Honeybee Face object")

    # z coordinate of the start and end of the rays
    z_receiver = receiver_face3d.max.z  # maximum z coordinate of the max (Point3D) of the Face receiver
    z_emitter = min([emitter_face3d.max.z, z_receiver])
    # start vertices, numpy arrays
    start_point_l = convert_point3d_to_numpy_array(emitter_face3d.lower_left_corner)
    start_point_r = convert_point3d_to_numpy_array(emitter_face3d.lower_right_corner)
    start_point_c = (start_point_l + start_point_r) / 2.
    start_point_l[2], start_point_l[2], start_point_c[
        2] = z_emitter, z_emitter, z_emitter  # correct the z coordinate
    # end vertices, numpy arrays
    end_point_l = convert_point3d_to_numpy_array(receiver_face3d.lower_left_corner)
    end_point_r = convert_point3d_to_numpy_array(receiver_face3d.lower_right_corner)
    end_point_c = (end_point_l + end_point_r) / 2.
    end_point_l[2], end_point_l[2], end_point_c[
        2] = z_receiver, z_receiver, z_receiver  # correct the z coordinate

    # ray list
    ray_list = [
        (start_point_c, end_point_c),
        (start_point_c, end_point_l),
        (start_point_c, end_point_r),
        (start_point_l, end_point_l),
        (start_point_r, end_point_r),
        (start_point_l, end_point_c),
        (start_point_r, end_point_c),
        (start_point_l, end_point_r),
        (start_point_r, end_point_l),
    ]

    correct_rays(ray_list=ray_list, face_receiver=face_receiver, exclude_surface_from_ray=exclude_surface_from_ray,
                 lower_ray_z_axis=lower_ray_z_axis)

    # if exclude_surface_from_ray:
    #     for i in range(number_of_rays):
    #         ray_list[i] = excluding_surfaces_from_ray(start_point=ray_list[i][0], end_point=ray_list[i][1])
    # if lower_ray_z_axis:  # todo @Elie: DO SOMETHING ABOUT THIS
    #     for i in range(number_of_rays):
    #         ray_list[i] = (ray_list[i][0] - np.array([0, 0, 0.1]), ray_list[i][1] - np.array([0, 0, 0.1]))

    return ray_list[:number_of_rays]


def excluding_surfaces_from_ray(start_point, end_point):
    """
        Return the start and end point of a ray reducing slightly the distance between the vertices to prevent
        considering the sender and receiver in the raytracing obstruction detection
        :param start_point: numpy array, start point of the ray
        :param end_point: numpy array, end point of the ray
        :return: new_start_point, new_end_point: numpy arrays, new start and end points of the ray
    """
    # todo @Elie: update
    ray_vector = end_point - start_point
    unit_vector = ray_vector / np.linalg.norm(ray_vector)  # normalize the vector with it's norm
    # Move the ray boundaries
    new_start_point = start_point + unit_vector * 0.05  # move the start vertex by 5cm on the toward the end vertex
    new_end_point = end_point - unit_vector * 0.05  # move the end vertex by 5cm on the toward the start vertex

    return new_start_point, new_end_point