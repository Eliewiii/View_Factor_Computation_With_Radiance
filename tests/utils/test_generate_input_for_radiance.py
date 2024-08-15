"""

"""

import os
import pytest

from current_development.vf_computation_with_radiance.vf_computation_with_radiance.utils import \
    from_polydata_to_dot_rad_str, from_rad_str_to_rad_file, from_rad_str_list_to_rad_file

from pyvista import PolyData

point_a = [1., 0., 0.]
point_b = [1., 1., 0.]
point_c = [0., 1., 0.]
point_d = [0., 0., 0.]
polydata_1 = PolyData([point_a, point_b, point_c, point_d])

point_a = [1., 0., 0.]
point_b = [1., 1., 0.]
point_c = [0., 1., 0.]
point_d = [-1., 0., 0.]
point_e = [0., 0., 0.]
polydata_2 = PolyData([point_a, point_b, point_c, point_d, point_e])




def test_from_polydata_to_dot_rad_str():
    """

    """
    identifier = "test_1"
    rad_file_content = from_polydata_to_dot_rad_str(polydata_1, identifier)
    print(rad_file_content)
    identifier = "test_2"
    rad_file_content = from_polydata_to_dot_rad_str(polydata_2, identifier)
    print(rad_file_content)


def test_from_polydata_to_rad_file():
    """

    """
    current_directory = os.path.dirname(__file__)

    path_rad_file = os.path.join(current_directory, "generated_file", "rad_1.rad")
    identifier = "test_1"
    from_rad_str_to_rad_file(from_polydata_to_dot_rad_str(polydata_1, identifier), path_rad_file)

    path_rad_file = os.path.join(current_directory, "generated_file", "rad_2.rad")
    identifier = "test_2"
    from_rad_str_to_rad_file(from_polydata_to_dot_rad_str(polydata_2, identifier), path_rad_file)


def test_from_polydata_list_to_rad_file():
    """

    """
    current_directory = os.path.dirname(__file__)

    path_rad_file = os.path.join(current_directory, "generated_file", "rad_3.rad")
    identifier_list = ["test_1", "test_2"]
    polydata_list = [polydata_1, polydata_2]
    from_rad_str_list_to_rad_file([from_polydata_to_dot_rad_str(polydata, identifier) for polydata, identifier in
                                   zip(polydata_list, identifier_list)], path_rad_file)
