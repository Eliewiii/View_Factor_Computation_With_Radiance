"""
Example file for the definition of radiative surfaces, RaditiveSurface objects used for view factor computation.
"""

from pyvista import PolyData

from radiance_comp_vf import RadiativeSurface

# Sample Polydata for testing
point_a = [1., 0., 0.]
point_b = [1., 1., 0.]
point_c = [0., 1., 0.]
point_d = [0., 0., 0.]
polydata_obj_1 = PolyData([point_a, point_b, point_c, point_d])