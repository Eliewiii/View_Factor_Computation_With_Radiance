# Radiance Comp VF

**Radiance Comp VF** is a Python package designed to compute the view factors between surfaces using Radiance.
This package simplifies complex radiative computations for various engineering and architectural applications.

The package is still under construction. Most of the key features are already implemented,
but the consideration of obstructions for instance is not fully operational.

The package requires predefine geometry in the Polydata format from the PyVista package. The view factors
to compute need to be predifined by the user: an additional package to select automatically the view factors
to compute will be implemented in the future.

## Features

**Implemented**:

- Automatic generation of the Radiance input files;
- Automatic parallel VF computation using Radiance;

**To be implemented**:

- Obstruction consideration (generation of octree files) (considered automatically by Radiance if less than
  100, see the Radiance Comp VF documentation when it will be available);
  -Automatic selection of the view factors to compute, for now the user has to define them manually
  (or with its custom algorithm). If less than 1000 surfaces, all surfaces can be considered as seeing each
  other, the computation time will still remain acceptable (less than 30 minutes on recent hardware ≈ 1 million view
  factor to compute).

## Installation

You can install the package directly from GitHub using `pip`:

```bash
pip install git+https://github.com/Eliewiii/View_Factor_Computation_With_Radiance.git
```

Or, if you have cloned the repository locally:

```bash
pip install .
```

## Usage

Here's a quick example to get you started:

```python

from radiance_comp_vf import RadiativeSurfaceManager

# Initialize the manager
manager = RadiativeSurfaceManager()

# Define surfaces and compute view factors
surface1 = ...
surface2 = ...
view_factor = manager.compute_view_factor(surface1, surface2)

print(f"View Factor: {view_factor}")
```

For more detailed usage, check the documentation.
Dependencies

This package requires the following Python packages:

    numpy
    pyvista
    radiance

You can install all dependencies using:

bash

pip install -r requirements.txt

Development

If you want to contribute to this project, follow these steps:

    Clone the repository:

    bash

git clone https://github.com/Eliewiii/View_Factor_Computation_With_Radiance.git

Install the package in development mode:

bash

pip install -e .[dev]

Run the tests:

bash

    pytest

License

This project is licensed under the MIT License - see the LICENSE file for details.
Contact

For any questions, feel free to reach out:

* Author: Elie MEIDONI
* Email: elie.medioniwii@gmail.com

Acknowledgments

    Acknowledge any libraries, tutorials, or collaborators that helped you in developing this package.

markdown
