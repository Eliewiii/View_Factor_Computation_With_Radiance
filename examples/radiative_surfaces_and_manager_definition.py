"""
Example file for the definition of radiative surfaces, RaditiveSurface objects used for view factor computation.
"""

from pyvista import PolyData

from radiance_comp_vf import RadiativeSurface, RadiativeSurfaceManager

# Sample Polydata for testing
point_a_1 = [1., 0., 0.]
point_b_1 = [1., 1., 0.]
point_c_1 = [0., 1., 0.]
point_d_1 = [0., 0., 0.]
polydata_obj_1 = PolyData([point_a_1, point_b_1, point_c_1, point_d_1])
identifier_polydata_1 = "surface_1"

# Sample Polydata for testing
point_a_2 = [1., 0., 1.]
point_d_2 = [0., 0., 1.]
point_c_2 = [0., 1., 1.]
point_b_2 = [1., 1., 1.]
polydata_obj_2 = PolyData([point_a_2, point_b_2, point_c_2, point_d_2])
identifier_polydata_2 = "surface_2"

# Make RadiativeSurface objects from PolyData
radiative_surface_obj_1 = RadiativeSurface.from_polydata(identifier_polydata_1, polydata_obj_1)
radiative_surface_obj_2 = RadiativeSurface.from_polydata(identifier_polydata_2, polydata_obj_2)

# Add viewed surfaces to the two RadiativeSurface objects
radiative_surface_obj_1.add_viewed_surfaces([identifier_polydata_2])
radiative_surface_obj_2.add_viewed_surfaces([identifier_polydata_1])

print(
    f"RadiativeSurface 1: {radiative_surface_obj_1}, "
    f"viewed surfaces: {[surface for surface in radiative_surface_obj_1.get_viewed_surfaces_id_list()]}"
)
print(
    f"RadiativeSurface 2: {radiative_surface_obj_2}, "
    f"viewed surfaces: {[surface for surface in radiative_surface_obj_2.get_viewed_surfaces_id_list()]}"
)

# Initialize the RadiativeSurfaceManager object
radiative_surface_manager_obj = RadiativeSurfaceManager()
# Add the RadiativeSurface objects to the RadiativeSurfaceManager object
radiative_surface_manager_obj.add_radiative_surfaces(radiative_surface_obj_1, radiative_surface_obj_2)
""" 
The surfaces can be added one after an other in the function, or as a list, or 
even a combination of both if needed...
for instance:
radiative_surface_manager_obj.add_radiative_surfaces([radiative_surface_obj_1, radiative_surface_obj_2])
radiative_surface_manager_obj.add_radiative_surfaces(radiative_surface_obj_1, [radiative_surface_obj_2])
"""
print(f"RadiativeSurfaceManager: {radiative_surface_manager_obj}")

