# Radiance Comp VF

**Radiance Comp VF** is a Python package designed to compute the view factors between surfaces using Radiance.
This package simplifies complex radiative computations for various engineering and architectural applications.

The package is still under construction. Most of the key features are already implemented,
but the consideration of obstructions for instance is not fully operational.

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

You can install the package directly from GitHub using `pip`:

```bash
pip install git+https://github.com/Eliewiii/View_Factor_Computation_With_Radiance.git
```

## Usage

Examples of usage are available in the `examples` folder. For more detailed usage, check the documentation.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any questions, feel free to reach out:

* Author: Elie MEIDONI
* Email: elie.medioniwiii@gmail.com
