"""
This file is the main file for the computation of view factors. It reads the configuration JSON file and computes the view factors for the given configuration.
It is meant to be executed as script from the command line, but should be called only through a RadiativeSurfaceManager object itself.

This way, a new process with only the RadiativeSurfaceManager in memory is created, instead of duplicating the whole script and all its dependencies, which could lead to memory issues.
"""
import json

from radiance_comp_vf import RadiativeSurfaceManager






def main(config_file):
    """
    Main function for the computation of view factors. It reads the configuration JSON file and computes the view factors for the given configuration.
    The following steps are performed:
    1. Read the configuration JSON file.
    2. Create load the existing RadiativeSurfaceManager object from pkl file.
    4. Perform the visibility check among surfaces.
    5. Generate the input files for the Radiance simulation and prepare the command line to run all these files.
    6. Run the Radiance simulation and extract the outputs from command line.
    7. Post process the outputs to readjust the view factors if specified and necessary.
    8. Generate view factor matrix and save it to a file.
    :param config_file:
    :return:
    """
    # Read the configuration JSON
    with open(config_file, 'r') as f:
        config = json.load(f)






    print("Parallel computation results:", results)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Please provide the configuration JSON file.")
    else:
        main(sys.argv[1])