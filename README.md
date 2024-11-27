# Radiance Comp VF

*Radiance Comp VF* is a Python package designed to compute the view factors between surfaces using Radiance.
This package simplifies complex radiative computations for various engineering and architectural applications.

The package is still under construction. Most of the key features are already implemented, but some instability ,might 
remain, as well as suboptimal performance. The package is still in development and will be updated regularly.

No stable release is available yet, but you can install the package from the last release tag and test it. Any feedback
is welcome.

## Features

**Implemented**:

- Automatic generation of the Radiance input files;
- Automatic parallel VF computation using Radiance;

**To be implemented**:

- Additional surface type support, for now only Polydata (Pyvista) is supported, soon to be added:
  - Honeybee surfaces;
- Obstruction consideration (generation of octree files) (considered automatically by Radiance if less than
  100, see the Radiance Comp VF documentation when it will be available);
- Automatic selection of the view factors to compute, for now the user has to define them manually
  (or with its custom algorithm). If less than 1000 surfaces, all surfaces can be considered as seeing each
  other, the computation time will still remain acceptable (less than 30 minutes on recent hardware ≈ 1
  million view
  factor to compute).

## Pre-requisites

The software need to be installed on your computer. You can install it from the official website:
https://www.radiance-online.org/download-install

You also need to add the Radiance bin folder (C:\Radiance\bin) to your PATH environment variable, as well as
creating the RAYPATH variable to the lib folder (C:\Radiance\lib).

## Installation

You can install the package directly from GitHub using `pip` if you have git installed:

```bash
pip install git+https://github.com/Eliewiii/View_Factor_Computation_With_Radiance.git
```

Or by pointing to the tar.gz file:

```bash
pip install https://github.com/Eliewiii/View_Factor_Computation_With_Radiance/archive/refs/tags/last_release_tag.tar.gz
```

## Usage

Examples of usage are available in the `examples` folder. For more detailed usage, check the documentation.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any questions, feel free to reach out:

* Author: Elie MEIDONI
* Email: elie.medioniwiii@gmail.com

## To Do list
- In the source code:
  - Add more checks to ensure the user inputs are correct, without adding to much complexity/computation time
  - Add more error handling
  - Add some checks to ensure the Radiance software is installed on the user's computer and can be called.
- In the tests:
  - Clean the test files to remove deprecated tests
  - Add new tests to check extreme cases
- In the documentation:
  - Add the documentation
- Performance optimization:
  - Perform more in-depth performance tests, especially to check if threading or multiprocessing is more efficient, 
  and in which conditions (especially for HPC).
  - Sensitivity analysis on the parameters to optimize the results/computation time, especially :
    - Visibility parameters, and the use of the minimum view factor criterion.
    - The number of rays to use in Radiance for optimal VF/compuation time, as computation increase exponentially with
    the number of rays.
  - Find a proper procedure to make sure windows defender or other antivirus software does not slow down the Radiance 
  simulation. The task manager shows an insane use (more than 70% of the CPU) of the antivirus software during the
  simulation using Radiance, which must slows down the simulation. This issue is specific to Windows.
    
