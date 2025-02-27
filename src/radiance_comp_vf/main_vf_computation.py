"""
This file is the main file for the computation of view factors. It reads the configuration JSON file and computes the view factors for the given configuration.
It is meant to be executed as script from the command line, but should be called only through a RadiativeSurfaceManager object itself.

This way, a new process with only the RadiativeSurfaceManager in memory is created, instead of duplicating the whole script and all its dependencies, which could lead to memory issues.
"""
import json
import logging

from time import time

from radiance_comp_vf import RadiativeSurfaceManager


def main(config_file):
    """
    Main function for the computation of view factors. It reads the configuration JSON file and computes the view factors for the given configuration.
    The following steps are performed:
    1. Read the configuration JSON file.
    2. Load the existing RadiativeSurfaceManager object from pkl file.
    3. Perform the visibility check among surfaces.
    4. Generate the input files for the Radiance simulation and prepare the command line to run all these files.
    5. Run the Radiance simulation and extract the outputs from command line.
    6. Post process the outputs to readjust the view factors if specified and necessary.
    7. Generate view factor matrix and save it to a file.
    :param config_file:
    :return:
    """
    # Read the configuration JSON
    logging.info(f"Reading configuration file: {config_file}")
    with open(config_file, 'r') as f:
        config_dict = json.load(f)

    # Load the existing RadiativeSurfaceManager object from pkl file
    logging.info(
        f"Loading RadiativeSurfaceManager object from pkl file: {config_dict['path_radiative_surface_manager_pkl']}")
    radiative_surface_manager_obj = RadiativeSurfaceManager.from_pkl(
        path_pkl_file=config_dict['path_radiative_surface_manager_pkl'])

    logging.info(
        f"Number of surfaces : {radiative_surface_manager_obj.num_surface}")

    # Perform the visibility check among surfaces
    duration = time()
    logging.info("Performing visibility check among surfaces...")
    radiative_surface_manager_obj.check_surface_visibility(
        num_workers=config_dict["num_worker_cpu_bound"],
        mvfc_check=config_dict["mvfc_check"],
        mvfc=config_dict["mvfc"],
        num_rays=config_dict["num_rays"],
        ray_traced_check=config_dict["ray_traced_check"],
        ray_tracing_among_all_corners=config_dict["ray_tracing_among_all_corners"])
    logging.info(f"Visibility check among surfaces completed in {time() - duration:.2f} seconds.")

    # Generate the input files for the Radiance simulation and prepare the command line to run all these files
    logging.info("Generating input files for the Radiance simulation and preparing the command line...")
    radiative_surface_manager_obj.generate_radiance_inputs_for_all_surfaces_in_parallel(
        path_root_simulation_folder=config_dict["path_simulation_folder"],
        num_receiver_per_file=config_dict["num_receiver_per_file"],
        num_workers=config_dict["num_worker_io_bound"],
        overwrite_folders=config_dict["overwrite_folders"],
        consider_octree=config_dict["consider_octree"],
        one_octree_for_all=config_dict["one_octree_for_all"],
    )

    # Run the Radiance simulation and extract the outputs from command line
    duration = time()
    logging.info("Running the Radiance simulation and extracting the outputs from command line...")
    radiative_surface_manager_obj._run_radiance_vf_computation_in_parallel_without_output_files(
        num_rays=config_dict["num_rays"],
        num_workers=config_dict["num_worker_cpu_bound"]
    )
    logging.info(f"Radiance simulation completed in {time() - duration:.2f} seconds.")
    #
    # # Post process the outputs to readjust the view factors if specified and necessary
    # logging.info("Post processing the outputs to readjust the view factors if specified and necessary...")
    # radiative_surface_manager_obj.post_process_outputs()
    #

    duration = time()
    logging.info("Generating view factor matrix and saving it to a file...")
    radiative_surface_manager_obj.save_vf_eps_rho_and_tau_matrices_to_npz(path_dir=config_dict["path_result_folder"])
    logging.info(f"View factor matrix generated and saved in {time() - duration:.2f} seconds.")

    # if config_dict["save_to_pkl"]:
    #     logging.info("Saving the updated RadiativeSurfaceManager object to a pkl file...")
    #     radiative_surface_manager_obj.to_pkl(path_folder=config_dict["path_result_folder"])


if __name__ == "__main__":

    import sys

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,  # Set the minimum logging level (DEBUG, INFO, WARNING, etc.)
        format="%(asctime)s - %(message)s"  # Customize your log message format
    )
    # Check if the configuration JSON file is provided
    if len(sys.argv) < 2:
        print("Please provide the configuration JSON file.")
    else:
        main(sys.argv[1])
