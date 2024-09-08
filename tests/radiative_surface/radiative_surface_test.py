"""
Test functions for the RadiativeSurface class.
"""
import pytest

from copy import deepcopy

from pyvista import PolyData
from shapely import centroid
from vtkmodules.generate_pyi import identifier

from src.radiance_comp_vf import RadiativeSurface

# Sample Polydata for testing
point_a = [1., 0., 0.]
point_b = [1., 1., 0.]
point_c = [0., 1., 0.]
point_d = [0., 0., 0.]
polydata_obj_1 = PolyData([point_a, point_b, point_c, point_d])

# Sample surface
surface_0 = [
    [0., 0., 0.],
    [10., 0., 0.],
    [10., 10., 0.],
    [0., 10., 0.]
]
area_surface_0 = 100
centroid_surface_0 = [5., 5., 0.]



@pytest.fixture(scope='function')
def radiative_surface_instance(request):
    num_instances = request.param if hasattr(request, 'param') else 1  # Default to 1 if no param
    if num_instances == 1:
        radiative_surface_instance_id = "identifier"
        instance = RadiativeSurface(radiative_surface_instance_id)
        return instance
    else:
        instance_list = []
        for i in range(num_instances):
            radiative_surface_instance_id = f"surface_{i}"
            instance_list.append(RadiativeSurface.from_polydata(radiative_surface_instance_id, polydata_obj_1))

        return instance_list


class TestRadiativeSurface:

    def test_init_radiative_surface(self):
        """
        Test the initialization of the RadiativeSurface class.
        """
        radiative_surface = RadiativeSurface("identifier")
        assert radiative_surface.identifier == "identifier"
        assert radiative_surface.origin_identifier == "identifier"
        assert radiative_surface.polydata_geometry is None
        assert radiative_surface._viewed_surfaces_id_list == []
        assert radiative_surface._viewed_surfaces_view_factor_list == []
        assert radiative_surface.emissivity is None
        assert radiative_surface.reflectivity is None
        assert radiative_surface.transmissivity is None
        assert radiative_surface.rad_file_content is None

    def test_init_radiative_surface_with_identifier_with_forbidden_characters(self):
        """
        Test the initialization of the RadiativeSurface class with an identifier containing forbidden characters and
        and invalid identifier (that cannot be adjusted automatically by the .
        """
        identifier = "identifier with spaces:and-forbidden_characters"
        radiative_surface = RadiativeSurface(identifier=identifier)
        assert radiative_surface.identifier == "identifier_with_spaces_and_forbidden_characters"
        assert radiative_surface.origin_identifier == identifier
        # Only invalid characters or underscores
        identifier = "_;.--_"
        with pytest.raises(ValueError):
            radiative_surface = RadiativeSurface(identifier=identifier)

    def test_set_radiative_properties(self):
        identifier = "test surface 1"
        # Test with valid values
        radiative_surface = RadiativeSurface(identifier=identifier)
        emissivity = 0.5
        reflectivity = 0.3
        transmissivity = 0.2
        radiative_surface.set_radiative_properties(emissivity=emissivity, reflectivity=reflectivity,
                                                   transmissivity=transmissivity)
        assert radiative_surface.emissivity == emissivity
        assert radiative_surface.reflectivity == reflectivity
        assert radiative_surface.transmissivity == transmissivity
        # Test with only emissivity
        radiative_surface = RadiativeSurface(identifier=identifier)
        emissivity = 0.5
        radiative_surface.set_radiative_properties(emissivity=emissivity)
        assert radiative_surface.emissivity == emissivity
        assert radiative_surface.reflectivity == 1 - emissivity
        assert radiative_surface.transmissivity == 0.
        # Test with reflectivity an emissivity
        radiative_surface = RadiativeSurface(identifier=identifier)
        emissivity = 0.5
        reflectivity = 0.3
        radiative_surface.set_radiative_properties(emissivity=emissivity, reflectivity=reflectivity)
        assert radiative_surface.emissivity == emissivity
        assert radiative_surface.reflectivity == reflectivity
        assert radiative_surface.transmissivity == 1 - emissivity - reflectivity
        # Test with  invalid values
        radiative_surface = RadiativeSurface(identifier=identifier)
        emissivity = -0.5
        with pytest.raises(ValueError):
            radiative_surface.set_radiative_properties(emissivity=emissivity)
        emissivity = 1.5
        with pytest.raises(ValueError):
            radiative_surface.set_radiative_properties(emissivity=emissivity)
        emissivity = 0.5
        reflectivity = 0.5
        transmissivity = 0.5
        with pytest.raises(ValueError):
            radiative_surface.set_radiative_properties(emissivity=emissivity, reflectivity=reflectivity,
                                                       transmissivity=transmissivity)

    def test_from_vertex_list(self):
        radiative_surface_object= RadiativeSurface.from_vertex_list("identifier", vertex_list=surface_0)
        # assert radiative_surface_object.




    def test_from_polydata(self):
        """
        Test the from_polydata method of the RadiativeSurface class.
        """
        radiative_surface = RadiativeSurface.from_polydata("identifier", polydata_obj_1)
        assert radiative_surface.identifier == "identifier"
        assert radiative_surface.origin_identifier == "identifier"
        assert radiative_surface.polydata_geometry == polydata_obj_1
        assert radiative_surface.viewed_surfaces_id_list == []
        assert radiative_surface.viewed_surfaces_view_factor_list == []
        assert radiative_surface.emissivity is None
        assert radiative_surface.reflectivity is None
        assert radiative_surface.transmissivity is None
        assert radiative_surface.rad_file_content is not None

        # Check the content of the rad file
        assert "identifier" in radiative_surface.rad_file_content
        assert "polygon" in radiative_surface.rad_file_content
        assert "void glow" in radiative_surface.rad_file_content
        assert str(len([point_a, point_b, point_c, point_d]) * 3) in radiative_surface.rad_file_content

        # Check with wrong input data
        with pytest.raises(ValueError):
            RadiativeSurface.from_polydata("identifier", "wrong_input")

    def test_deepcopy(self, radiative_surface_instance):
        """
        Test the deepcopy method of the RadiativeSurface class.
        """
        radiative_surface = radiative_surface_instance
        new_radiative_surface = deepcopy(radiative_surface)
        assert new_radiative_surface.identifier == radiative_surface.identifier
        assert new_radiative_surface.origin_identifier == radiative_surface.origin_identifier
        assert new_radiative_surface.polydata_geometry == radiative_surface.polydata_geometry
        assert new_radiative_surface.viewed_surfaces_view_factor_list == radiative_surface.viewed_surfaces_view_factor_list
        assert new_radiative_surface.viewed_surfaces_id_list == radiative_surface.viewed_surfaces_id_list
        assert new_radiative_surface.viewed_surfaces_id_list is not radiative_surface.viewed_surfaces_id_list
        assert new_radiative_surface.viewed_surfaces_view_factor_list is not radiative_surface.viewed_surfaces_view_factor_list
        assert new_radiative_surface.emissivity == radiative_surface.emissivity
        assert new_radiative_surface.reflectivity == radiative_surface.reflectivity
        assert new_radiative_surface.transmissivity == radiative_surface.transmissivity
        assert new_radiative_surface.rad_file_content == radiative_surface.rad_file_content

    def test_add_viewed_face(self, radiative_surface_instance):
        """
        Test the add_viewed_face method of the RadiativeSurface class.
        """
        radiative_surface = radiative_surface_instance
        # Add 2 viewed surface
        radiative_surface.add_viewed_surfaces(["viewed_surface_1", "viewed_surface_2"])
        assert radiative_surface.get_viewed_surfaces_id_list() == ["viewed_surface_1", "viewed_surface_2"]
        assert radiative_surface.viewed_surfaces_view_factor_list == []
        # Try to add the same viewed surface
        with pytest.raises(ValueError):
            radiative_surface.add_viewed_surfaces(["viewed_surface_1"])

    def test_generate_rad_file_name(self, radiative_surface_instance):
        """
        Test the generate_rad_file_name method of the RadiativeSurface class.
        """
        radiative_surface = radiative_surface_instance
        name_emitter_rad_file, name_receiver_rad_file, name_output_file = radiative_surface.generate_rad_file_name()
        assert name_emitter_rad_file == f"emitter_{radiative_surface.identifier}"
        assert name_receiver_rad_file == f"receiver_{radiative_surface.identifier}_batch_"
        assert name_output_file == f"output_{radiative_surface.identifier}_batch_"

    def test_from_random_rectangles(self):
        """
        Test the from_random_rectangles method of the RadiativeSurface class.
        """
        # todo
        # radiative_surface = RadiativeSurface.from_random_rectangles()
        # assert radiative_surface.identifier == "random_rectangle"
        # assert radiative_surface.origin_identifier is None
        # assert radiative_surface.polydata_geometry is not None
        # assert radiative_surface.viewed_surfaces_id_list == []
        # assert radiative_surface.viewed_surfaces_view_factor_list == []
        # assert radiative_surface.emissivity is None
        # assert radiative_surface.reflectivity is None
        # assert radiative_surface.transmissivity is None
        # assert radiative_surface.rad_file_content is not None
