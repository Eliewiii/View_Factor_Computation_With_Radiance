"""

"""
import os

from pyvista import PolyData

from typing import List

from current_development.vf_computation_with_radiance.vf_computation_with_radiance.utils.utils_folder_manipulation import check_parent_folder_exist


def from_emitter_receiver_to_rad_files(emitter_polydata: PolyData, emitter_id: str,
                                       receiver_polydata_list: List[PolyData], receiver_id_list: List[str],
                                       path_emitter_folder: str,
                                       path_receiver_folder: str, path_output_folder: str,
                                       batch_index_emitter: int) -> (str, str, str):
    """
    Convert the emitter and receiver PolyData to Radiance files.
    :param emitter_polydata: PolyData, the emitter polydata.
    :param emitter_id: str, the identifier of the emitter.
    :param receiver_polydata_list: [PolyData], the list of receiver polydata.
    :param receiver_id_list: [str], the list of identifiers of the receivers.
    :param path_emitter_folder: str, the path of the folder where to save the emitter Radiance file.
    :param path_receiver_folder: str, the path of the folder where to save the receiver Radiance files.
    :param path_output_folder: str, the path of the folder where to save the output files.
    :param batch_index_emitter: int, the index of the batch for the emitter due to the limit of simultaneous receivers
        Radiance accepts.
    :return path_emitter_rad_file: str, the path of the emitter Radiance file.
    :return path_receiver_rad_file_list: [str], the list of paths of the receiver Radiance files.
    :return path_output_file: [str], the list of paths of the output files.
    """
    # Generate the strings for the emitter and receivers Radiance files
    emitter_rad_str = from_polydata_to_dot_rad_str(emitter_polydata, emitter_id)
    receiver_rad_str_list = [from_polydata_to_dot_rad_str(receiver_polydata, receiver_id) for
                             receiver_polydata, receiver_id in zip(receiver_polydata_list, receiver_id_list)]
    # Generate the paths of the Radiance files
    path_emitter_rad_file = os.path.join(path_emitter_folder, f"emitter_{emitter_id}_{batch_index_emitter}.rad")
    path_receiver_rad_file_list = os.path.join(path_receiver_folder,
                                               f"receiver_for_{emitter_id}_batch_{batch_index_emitter}.rad")
    path_output_file = os.path.join(path_output_folder, f"output_{emitter_id}_{batch_index_emitter}.txt")
    # Generate the files
    from_emitter_receiver_rad_str_to_rad_files(emitter_rad_str=emitter_rad_str,
                                               receiver_rad_str_list=receiver_rad_str_list,
                                               path_emitter_rad_file=path_emitter_folder,
                                               path_receiver_rad_file=path_receiver_folder)

    return path_emitter_rad_file, path_receiver_rad_file_list, path_output_file


def from_emitter_receiver_rad_str_to_rad_files(emitter_rad_str: str,
                                               receiver_rad_str_list: List[PolyData],
                                               path_emitter_rad_file: str,
                                               path_receiver_rad_file: str):
    """
    Convert the emitter and receiver PolyData to Radiance files.
    :param emitter_rad_str: PolyData, the emitter polydata.
    :param emitter_id: str, the identifier of the emitter.
    :param receiver_rad_str_list: [PolyData], the list of receiver polydata.
    :param path_emitter_rad_file: str, the path file of the emitter Radiance file.
    :param path_receiver_rad_file: str, the path of the receiver Radiance file.
    """
    # Generate the receiver Radiance files
    from_rad_str_to_rad_file(rad_str=emitter_rad_str, path_rad_file=path_emitter_rad_file)
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
