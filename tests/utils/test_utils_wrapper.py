"""

"""

from src.radiance_comp_vf.radiative_surface import RadiativeSurface
from src.radiance_comp_vf.utils import object_method_wrapper


def test_object_wrapper():
    """
    Test the object_method_wrapper function.
    """
    radiative_surface = RadiativeSurface("identifier")
    method_name = "add_viewed_surfaces"

    emitter_id="emitter_identifier"
    object_method_wrapper(radiative_surface, method_name,[emitter_id])
    assert radiative_surface.viewed_surfaces_id_list == [emitter_id]

