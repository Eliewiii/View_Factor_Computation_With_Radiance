"""
This file is the main file for the computation of view factors. It reads the configuration JSON file and computes the view factors for the given configuration.
It is meant to be executed as script from the command line, but should be called only through a RadiativeSurfaceManager object itself.

This way, a new process with only the RadiativeSurfaceManager in memory is created, instead of duplicating the whole script and all its dependencies, which could lead to memory issues.
"""
import json
import logging

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
        config = json.load(f)
    # Load the existing RadiativeSurfaceManager object from pkl file
    logging.info(f"Loading RadiativeSurfaceManager object from pkl file: {config['rsm_pkl_file']}")
    radiative_surface_manager_obj = RadiativeSurfaceManager.from_pkl(path_pkl_file=config['rsm_pkl_file'])
    # Perform the visibility check among surfaces
    logging.info("Performing visibility check among surfaces...")
    radiative_surface_manager_obj.perform_visibility_check()
    # Generate the input files for the Radiance simulation and prepare the command line to run all these files
    logging.info("Generating input files for the Radiance simulation and preparing the command line...")
    radiative_surface_manager_obj.generate_input_files_for_radiance_simulation()
    # Run the Radiance simulation and extract the outputs from command line
    logging.info("Running the Radiance simulation and extracting the outputs from command line...")
    radiative_surface_manager_obj.run_radiance_simulation()
    # Post process the outputs to readjust the view factors if specified and necessary
    logging.info("Post processing the outputs to readjust the view factors if specified and necessary...")
    radiative_surface_manager_obj.post_process_outputs()
    # Generate view factor matrix and save it to a file
    logging.info("Generating view factor matrix and saving it to a file...")
    radiative_surface_manager_obj.generate_view_factor_matrix()







    print("Parallel computation results:", results)


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

