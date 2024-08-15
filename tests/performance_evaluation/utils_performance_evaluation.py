"""
Script to evaluate the performance of the RadiativeSurfaceManager VF computation with Radiance,
using various parameters for parallel computing for large datasets.
"""
import os

from time import time

from concurrent.futures import ThreadPoolExecutor

from src.vf_computation_with_radiance import RadiativeSurfaceManager

# from ...vf_computation_with_radiance import RadiativeSurfaceManager
from src.vf_computation_with_radiance import create_folder


def generate_radiance_files_in_parallel(radiative_surface_manager_obj, rad_sim_folder,
                                        num_receiver_per_file=5):
    """
    Test the generate_radiance_files method of the RadiativeSurfaceManager class.
    """
    dur = time()
    # Initialize the radiative surface manager and folders
    path_emitter_folder, path_receiver_folder, path_output_folder = set_up_folders_for_radiance_files(
        rad_sim_folder)
    # Generate the files
    num_workers = 4
    worker_batch_size = 10
    radiative_surface_manager_obj.generate_radiance_inputs_for_all_surfaces_in_parallel(
        path_emitter_folder=path_emitter_folder,
        path_receiver_folder=path_receiver_folder,
        path_output_folder=path_output_folder,
        num_receiver_per_file=num_receiver_per_file,
        num_workers=num_workers,
        worker_batch_size=worker_batch_size,
        executor_type=ThreadPoolExecutor
    )
    return time() - dur


def init_radiative_surface_manager(num_ref_rectangles=1,
                                   num_random_rectangle=1,
                                   min_size=0.1, max_size=10,
                                   max_distance_factor=10):
    """

    """

    radiative_surface_manager_obj = RadiativeSurfaceManager.from_random_rectangles(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=min_size, max_size=max_size,
        max_distance_factor=max_distance_factor,
        parallel_coaxial_squares=False
    )
    return radiative_surface_manager_obj


def init_radiative_surface_manager_in_parallel(num_ref_rectangles=1,
                                               num_random_rectangle=1,
                                               min_size=0.1, max_size=10,
                                               max_distance_factor=10,
                                               num_workers=4,
                                               worker_batch_size=1,
                                               executor_type=ThreadPoolExecutor):
    """

    """

    radiative_surface_manager_obj = RadiativeSurfaceManager.from_random_rectangles_in_parallel(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=min_size, max_size=max_size,
        max_distance_factor=max_distance_factor,
        parallel_coaxial_squares=False,
        num_workers=num_workers,
        worker_batch_size=worker_batch_size,
        executor_type=executor_type
    )
    return radiative_surface_manager_obj


def init_radiative_surface_manager_from_random_rectangles_that_see_each_others(num_rectangles=1,
                                                                               min_size=0.1, max_size=10,
                                                                               max_distance_factor=10):
    """

    """

    radiative_surface_manager_obj = RadiativeSurfaceManager.from_random_rectangles_that_see_each_others(
        num_rectangles=num_rectangles,
        min_size=min_size, max_size=max_size,
        max_distance_factor=max_distance_factor,
        parallel_coaxial_squares=False,
    )
    return radiative_surface_manager_obj


def set_up_folders_for_radiance_files(rad_sim_folder):
    """

    """
    create_folder(rad_sim_folder, overwrite=False)
    # Paths to emitter, receiver and output directory
    path_emitter_folder = os.path.join(rad_sim_folder, "emitter")
    path_receiver_folder = os.path.join(rad_sim_folder, "receiver")
    path_output_folder = os.path.join(rad_sim_folder, "output")
    return path_emitter_folder, path_receiver_folder, path_output_folder


def run_vf_computation(radiative_surface_manager_obj, type: str, nb_rays=10000,
                       command_batch_size=1,
                       num_workers=1,
                       worker_batch_size=1,
                       executor_type=ThreadPoolExecutor):
    """

    """
    dur = time()
    if type == "single":
        radiative_surface_manager_obj.run_vf_computation(
            nb_rays=nb_rays
        )
    elif type == "parallel":
        radiative_surface_manager_obj.run_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=executor_type
        )
    elif type == "parallel_grouped_commands":
        radiative_surface_manager_obj.run_vf_computation_in_parallel_with_grouped_commands(
            nb_rays=nb_rays,
            command_batch_size=command_batch_size,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=executor_type
        )
    else:
        raise ValueError(f"Unknown type: {type}")

    return time() - dur
