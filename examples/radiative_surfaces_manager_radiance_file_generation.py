"""
Example file for the definition of radiative surfaces, RaditiveSurface objects used for view factor computation.
"""

from pyvista import PolyData

from radiance_comp_vf import RadiativeSurfaceManager

# Initialize the RadiativeSurfaceManager object with already random rectangles
radiative_surface_manager_obj = RadiativeSurfaceManager.from_random_rectangles_that_see_each_others(
    num_rectangles=10)

print(f"RadiativeSurfaceManager: {radiative_surface_manager_obj}")
print(
    f"Number of radiative surfaces: {len(radiative_surface_manager_obj.get_list_of_radiative_surface_id())}")

radiative_surface_rect_0 = radiative_surface_manager_obj.get_radiative_surface(
    identifier=radiative_surface_manager_obj.get_list_of_radiative_surface_id()[0])
print(f"{radiative_surface_rect_0} sees: {radiative_surface_rect_0.get_viewed_surfaces_id_list()} ")
