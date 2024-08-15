"""

"""
import os
from time import time

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from current_development.vf_computation_with_radiance.tests.performance_evaluation.utils_performance_evaluation import \
    generate_radiance_files_in_parallel, init_radiative_surface_manager, \
    run_vf_computation, RadiativeSurfaceManager


def main(path_simulation_manager_pkl, path_simulation_folder: str):
    """
    Main function to evaluate the performance of the VF computation
    :param path_simulation_folder: str, the path of the simulation folder.
    """
    # Input geometry
    n_vf=1000000
    # Input batch within receiver rad_files
    num_receiver_per_file = 100
    # Input vf computation
    nb_rays = 100000
    command_batch_size = 10
    num_workers = 10
    worker_batch_size = 11
    executor_type = ThreadPoolExecutor
    print(f"start init.")
    dur = time()
    radiative_surface_manager_obj = RadiativeSurfaceManager.from_pkl(path_simulation_manager_pkl)
    print(f"Duration init: {time() - dur}s.")
    print(f"file generation.")
    # Generate the radiance files in parallel
    dur = generate_radiance_files_in_parallel(radiative_surface_manager_obj,
                                              rad_sim_folder=path_simulation_folder,
                                              num_receiver_per_file=num_receiver_per_file)
    print(
        f"Duration file generation: {dur}s")
    print(f"start vf computation.")
    # Run the VF computation in parallel
    # dur = run_vf_computation(radiative_surface_manager_obj, type="single",
    #                          nb_rays=nb_rays,
    #                          command_batch_size=command_batch_size,
    #                          num_workers=num_workers,
    #                          worker_batch_size=worker_batch_size,
    #                          executor_type=executor_type)
    # print(f"Duration single thread: {dur}s for {num_ref_rectangles * num_random_rectangle} vf to compute.")

    dur = run_vf_computation(radiative_surface_manager_obj, type="parallel",
                             nb_rays=nb_rays,
                             command_batch_size=command_batch_size,
                             num_workers=num_workers,
                             worker_batch_size=worker_batch_size,
                             executor_type=ThreadPoolExecutor)
    print(f"Duration parallel Thread: {dur}s for {n_vf} vf to compute.")

    dur = run_vf_computation(radiative_surface_manager_obj, type="parallel",
                             nb_rays=nb_rays,
                             command_batch_size=command_batch_size,
                             num_workers=num_workers,
                             worker_batch_size=worker_batch_size,
                             executor_type=ProcessPoolExecutor)
    print(f"Duration parallel process: {dur}s for {n_vf} vf to compute.")

    # dur = run_vf_computation(radiative_surface_manager_obj, type="parallel",
    #                          nb_rays=nb_rays,
    #                          command_batch_size=command_batch_size,
    #                          num_workers=num_workers,
    #                          worker_batch_size=worker_batch_size,
    #                          executor_type=executor_type)
    # print(f"Duration parallel: {dur}s for {n_vf} vf to compute.")

    # dur = run_vf_computation(radiative_surface_manager_obj, type="parallel_grouped_commands",
    #                          nb_rays=nb_rays,
    #                          command_batch_size=command_batch_size,
    #                          num_workers=num_workers,
    #                          worker_batch_size=worker_batch_size,
    #                          executor_type=ProcessPoolExecutor)
    # print(
    #     f"Duration parallel grouped batch: {dur}s for {num_ref_rectangles * num_random_rectangle} vf to compute.")


if __name__ == "__main__":
    path_simulation_folder = r"D:\Elie\PhD\vf_computation\tests"
    path_simulation_manager_pkl = r"D:\Elie\PhD\vf_computation\radiative_surface_manager_l_40K.pkl"

    main(path_simulation_manager_pkl,path_simulation_folder)
