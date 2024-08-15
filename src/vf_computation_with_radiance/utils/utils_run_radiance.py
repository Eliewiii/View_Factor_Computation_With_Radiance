"""

"""

import os
import subprocess

from typing import List

from current_development.vf_computation_with_radiance.vf_computation_with_radiance.utils.utils_folder_manipulation import \
    check_parent_folder_exist, check_file_exist


def run_radiant_vf_computation_in_batches(*rad_argument_batch_list: List[List],
                                          path_octree_context_list: List[str] = None,
                                          nb_rays: int = 10000):
    """
    Compute the view factor between multiple emitter and receiver with Radiance in batches.
    :param rad_argument_batch_list: [[str, str, str]], the list of arguments for the Radiance computation.
    :param path_octree_context_list: [str], the list of paths of the octree files.
    :param nb_rays: int, the number of rays to use.
    """
    # Generate the commands
    command_list = []
    for rad_argument_batch in rad_argument_batch_list:
        command_list.append(write_radiance_command_for_vf_computation(*rad_argument_batch,
                                                                      # path_octree_context=path_octree_context,
                                                                      nb_rays=nb_rays))
    # Run the commands in batches
    run_command_in_batches(command_list)


def run_command_in_batches(command_list: List[str]):
    """
    Run a list of commands in batches.
    :param command_list: [str], the list of commands to run.
    :param command_batch_size: int, the size of the batch.
    """
    command = " & ".join(command_list)
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_radiance_command_for_vf_computation(path_emitter_rad_file: str, path_receiver_rad_file: str,
                                              path_output_file: str, path_octree_context: str = None,
                                              nb_rays: int = 10000):
    """
    Compute the view factor between 2 rectangles with Radiance.
    :param path_emitter_rad_file: str, the path of the emitter Radiance file.
    :param path_receiver_rad_file: str, the path of the receiver Radiance file.
    :param path_output_file: str, the path of the output file.
    :param path_octree_context: str, the path of the octree file.
    :param nb_rays: int, the number of rays to use.
    """
    # Check if the paths of emitter and receiver files exist
    check_file_exist(path_emitter_rad_file)
    check_file_exist(path_receiver_rad_file)
    # Check if the folder of the output file exists
    check_parent_folder_exist(path_output_file)
    # Check if the octree file exists if provided
    if path_octree_context and not os.path.exists(path_octree_context):
        raise FileNotFoundError(f"File not found: {path_octree_context}")
    # Compute the view factor
    command = f'rfluxmtx -h- -ab 0 -c {nb_rays} ' + f'"!xform -I "{path_emitter_rad_file}"" ' + (
        f'"{path_receiver_rad_file}"')
    if path_octree_context:
        command += f' "{path_octree_context}"'
    command += f' > "{path_output_file}"'

    return command


def compute_vf_between_emitter_and_receivers_radiance(path_emitter_rad_file: str,
                                                      path_receiver_rad_file: str,
                                                      path_output_file: str,
                                                      path_octree_context: str = "",
                                                      nb_rays: int = 10000):
    """
    Compute the view factor between 2 rectangles with Radiance.
    :param path_emitter_rad_file: str, the path of the emitter Radiance file.
    :param path_receiver_rad_file: str, the path of the receiver Radiance file.
    :param path_output_file: str, the path of the output file.
    :param path_octree_context: str, the path of the octree file.
    :param nb_rays: int, the number of rays to use.
    """

    command = write_radiance_command_for_vf_computation(path_emitter_rad_file, path_receiver_rad_file,
                                                        path_output_file, path_octree_context, nb_rays)

    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
