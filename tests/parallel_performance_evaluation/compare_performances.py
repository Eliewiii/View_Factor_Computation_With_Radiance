"""
This script is used to compare the performances of the parallel version of the code.
"""

import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import time
from math import ceil

from src.radiance_comp_vf import RadiativeSurfaceManager

# Geometry creation
def make_geo(num_rectangles:int):
    radiative_surface_manager_obj = RadiativeSurfaceManager.from_random_rectangles_that_see_each_others(
        num_rectangles=num_rectangles,
        min_size=0.5, max_size=2,
        max_distance_factor=10,
        parallel_coaxial_squares=False,
    )
    return radiative_surface_manager_obj


# Make input files
def make_inputs(radiative_surface_manager,path_root_simulation_folder,
            num_receiver_per_file):

    radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
        path_root_simulation_folder=path_root_simulation_folder,
        num_receiver_per_file=num_receiver_per_file,
        num_workers=16,
        worker_batch_size=10,
        executor_type=ThreadPoolExecutor
    )

# Run the simulation
def run_sim_with_outputs(radiative_surface_manager,nb_rays:int,
            num_workers:int,
            worker_batch_size:int,
            executor_type):
    radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )

def run_sim_without_outputs(radiative_surface_manager,nb_rays:int,
            num_workers:int,
            worker_batch_size:int,
            executor_type):
    radiative_surface_manager._run_radiance_vf_computation_in_parallel_without_output_files(
        nb_rays=nb_rays,
        num_workers=num_workers,
        worker_batch_size=worker_batch_size,
        executor_type=ProcessPoolExecutor
    )


def main():
    # Geometry creation
    num_ref_rectangles = 400
    radiative_surface_manager=make_geo(num_ref_rectangles)

    # Parallel parameters
    num_receiver_per_file = 100

    num_workers = 16
    # worker_batch_size = ceil(ceil((num_ref_rectangles-1) // 100)*num_ref_rectangles/num_workers)
    # print(f"worker_batch_size : {worker_batch_size}")
    worker_batch_size = 50

    # VF parameters
    nb_rays = 500000


    # Make input files
    file_dir = os.path.dirname(os.path.abspath(__file__))
    path_root_simulation_folder = os.path.join(file_dir, "outputs")


    make_inputs(radiative_surface_manager,path_root_simulation_folder,
            num_receiver_per_file)

    # Simulation with outputs and Threading
    start = time()
    run_sim_with_outputs(radiative_surface_manager,
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
    dur_with_outputs_threading = time() - start
    print(f"Simulation with outputs and threading : {dur_with_outputs_threading}")

    # Simulation with outputs and Threading and double the number of workers
    start = time()
    run_sim_with_outputs(radiative_surface_manager,
            nb_rays=nb_rays,
            num_workers=num_workers*2,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
    dur_with_outputs_threading = time() - start
    print(f"Simulation with outputs and threading : {dur_with_outputs_threading}")

    # Simulation with outputs and multiprocessing
    start = time()
    run_sim_with_outputs(radiative_surface_manager,
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
    dur_with_outputs_multiprocessing = time() - start
    print(f"Simulation with outputs and multiprocessing : {dur_with_outputs_multiprocessing}")

    # Simulation without outputs and Threading
    start = time()
    run_sim_without_outputs(radiative_surface_manager,
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
    dur_without_outputs_threading = time() - start
    print(f"Simulation without outputs and threading : {dur_without_outputs_threading}")

    # Simulation without outputs and Threading and double the number of workers
    start = time()
    run_sim_without_outputs(radiative_surface_manager,
            nb_rays=nb_rays,
            num_workers=num_workers*2,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
    dur_without_outputs_threading = time() - start
    print(f"Simulation without outputs and threading x2 : {dur_without_outputs_threading}")

    # Simulation without outputs and Threading and double the number of workers
    start = time()
    run_sim_without_outputs(radiative_surface_manager,
            nb_rays=nb_rays,
            num_workers=num_workers*3,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
    dur_without_outputs_threading = time() - start
    print(f"Simulation without outputs and threading x3 : {dur_without_outputs_threading}")

    # Simulation without outputs and multiprocessing
    start = time()
    run_sim_without_outputs(radiative_surface_manager,
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
    dur_without_outputs_multiprocessing = time() - start
    print(f"Simulation without outputs and multiprocessing : {dur_without_outputs_multiprocessing}")

if __name__ == "__main__":
    main()

