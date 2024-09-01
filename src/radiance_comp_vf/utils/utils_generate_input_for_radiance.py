"""

"""
import os

from pyvista import PolyData

from typing import List

from .utils_folder_manipulation import check_parent_folder_exist
from .utils_batches import split_into_batches
from .utils_run_radiance import run_oconv_command_for_octree_generation


def from_emitter_rad_str_to_rad_file(emitter_rad_str: str, path_emitter_rad_file: str):
    """
    Convert the emitter PolyData to a Radiance file.
    :param emitter_rad_str:
    :param path_emitter_rad_file:
    """
    from_rad_str_to_rad_file(rad_str=emitter_rad_str, path_rad_file=path_emitter_rad_file)


def from_receiver_rad_str_to_octree_file(receiver_rad_str_list: str, path_folder_octree: str,
                                         name_octree_file: str,
                                         num_receiver_per_octree: int) -> str:
    """
    Convert the emitter and receiver PolyData to Radiance files.
    :param receiver_rad_str_list: [str], the list of receiver polydata.
    :param path_folder_octree: str, the path of the folder to save the octree file.
    :param name_octree_file: str, the name of the octree file.
    :param num_receiver_per_octree: int, the number of receiver per rad file to convert to octree because
        of Radiance limitations.
    :return: str, the path of the octree file.
    """
    # Split the list of receiver PolyData into batches
    receiver_rad_str_list_batches = split_into_batches(receiver_rad_str_list, num_receiver_per_octree)
    num_batches = len(receiver_rad_str_list_batches)
    #
    name_rad_file_list = [name_octree_file + f"_batch_{i}" for i in range(num_batches)]
    path_rad_file_list = [os.path.join(path_folder_octree, name_rad_file + ".rad") for name_rad_file in
                          name_rad_file_list]
    path_octree_file = os.path.join(path_folder_octree, name_octree_file + ".oct")
    # Generate the initial rad file
    for receiver_rad_str_batch, path_rad_file in zip(receiver_rad_str_list_batches, path_rad_file_list):
        from_rad_str_list_to_octree_rad_file(rad_str_list=receiver_rad_str_batch, path_rad_file=path_rad_file)
    # Convert the rad files to octree file
    run_oconv_command_for_octree_generation(path_rad_file_list=path_rad_file_list,
                                            path_octree_file=path_octree_file)
    # # Delete the rad file
    # for path_rad_file in path_rad_file_list:
    #     os.remove(path_rad_file)

    return path_octree_file


def from_receiver_rad_str_to_rad_files(receiver_rad_str_list: List[str],
                                       path_receiver_rad_file: str):
    """
    Convert the emitter and receiver PolyData to Radiance files.
    :param receiver_rad_str_list: [str], the list of receiver polydata.
    :param path_receiver_rad_file: str, the path of the receiver Radiance file.
    """
    # Generate the receiver Radiance files
    from_rad_str_list_to_rad_file(rad_str_list=receiver_rad_str_list, path_rad_file=path_receiver_rad_file)


def from_rad_str_to_rad_file(rad_str: str, path_rad_file: str):
    """
    Convert a PolyData to a Radiance file.
    :param rad_str: str, the Radiance string of the surface.
    :param path_rad_file: str, the path of the Radiance file.
    """
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_rad_file)
    # Convert the PolyData to a Radiance file
    rad_file_content = r"#@rfluxmtx h=u" + "\n"
    rad_file_content += rad_str
    with open(path_rad_file, "w") as f:
        f.write(rad_file_content)


def from_rad_str_list_to_rad_file(rad_str_list: List[str], path_rad_file: str):
    """
    Convert a list of PolyData to a Radiance file.
    :param rad_str_list: [str], the list of Radiance strings of the surfaces.
    :param path_rad_file: str, the path of the Radiance file.
    """
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_rad_file)
    # Convert the PolyData to a Radiance file
    rad_file_content = r"#@rfluxmtx h=u" + "\n"
    for rad_str in rad_str_list:
        rad_file_content += rad_str
    with open(path_rad_file, "w") as f:
        f.write(rad_file_content)


def from_rad_str_list_to_octree_rad_file(rad_str_list: List[str], path_rad_file: str):
    """
    Convert a list of PolyData to a Radiance file.
    :param rad_str_list: [str], the list of Radiance strings of the surfaces.
    :param path_rad_file: str, the path of the Radiance file.
    """
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_rad_file)
    # Convert the PolyData to a Radiance file
    rad_file_content = ''
    for rad_str in rad_str_list:
        rad_file_content += rad_str
    with open(path_rad_file, "w") as f:
        f.write(rad_file_content)


def from_vertex_list_to_rad_str(vertices: List[List[float]], identifier: str) -> str:
    """
    Convert a list of vertices to a Radiance string to be saved in a .rad file.
    :param vertices: List[List[float]], the list of vertices.
    :param identifier: str, the identifier of the object.
    :return: str, the Radiance string.
    """
    rad_file_content = ""
    rad_file_content += f"void glow sur_{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"4 1 1 1 0" + "\n"
    rad_file_content += f"sur_{identifier} polygon surface.{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    nb_coords = len(vertices) * 3
    rad_file_content += (f"{nb_coords}")
    for v in vertices:
        rad_file_content += f" {v[0]} {v[1]} {v[2]}\n"

    return rad_file_content

def from_vertex_list_to_rad_str_to_test(vertices: List[List[float]], identifier: str) -> str:
    """
    Convert a list of vertices to a Radiance string to be saved in a .rad file.
    :param vertices: List[List[float]], the list of vertices.
    :param identifier: str, the identifier of the object.
    :return: str, the Radiance string.
    """
    rad_file_content = ""
    rad_file_content += f"void polygon surface.{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    nb_coords = len(vertices) * 3
    rad_file_content += (f"{nb_coords}")
    for v in vertices:
        rad_file_content += f" {v[0]} {v[1]} {v[2]}\n"

    return rad_file_content


def from_polydata_to_dot_rad_str(polydata: PolyData, identifier: str) -> str:
    """
    Convert a PolyData to a Radiance string to be saved in a .rad file.
    :param polydata: PolyData, the polydata to convert.
    :param identifier: str, the identifier of the object.
    :return: str, the Radiance string.
    """
    rad_file_content = ""
    vertices = polydata.points
    rad_file_content += f"void glow sur_{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"4 1 1 1 0" + "\n"
    rad_file_content += f"sur_{identifier} polygon surface.{identifier}" + "\n"
    rad_file_content += f"0" + "\n"
    rad_file_content += f"0" + "\n"
    nb_coords = len(vertices) * 3
    rad_file_content += (f"{nb_coords}")
    for v in vertices:
        rad_file_content += f" {v[0]} {v[1]} {v[2]}\n"

    return rad_file_content
