"""
Test the initialization of the RadiativeSurfaceManager object.
"""

import os
import pytest

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import time

from src.radiance_comp_vf import RadiativeSurface
from src.radiance_comp_vf import RadiativeSurfaceManager
from src.radiance_comp_vf.radiative_surface.radiative_surface_manager_class import flatten_table_to_lists

from tests.radiative_surface.radiative_surface_obj.radiative_surface_test import radiative_surface_instance

test_file_dir = os.path.dirname(os.path.abspath(__file__))

radiance_test_file_dir = os.path.join(os.path.dirname(test_file_dir), "radiance_test_files")


@pytest.fixture(scope='function')
def radiative_surface_manager_instance():
    radiative_surface_manager_instance = RadiativeSurfaceManager()
    return radiative_surface_manager_instance


num_ref_rectangles = 2
num_random_rectangle = 10
num_rectangles = 50


@pytest.fixture(scope='function')
def radiative_surface_manager_instance_with_random_rectangles():
    radiative_surface_manager_instance = RadiativeSurfaceManager.from_random_rectangles(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=0.1, max_size=10,
        max_distance_factor=10,
        parallel_coaxial_squares=False
    )
    return radiative_surface_manager_instance

@pytest.fixture(scope='function')
def radiative_surface_manager_instance_with_random_rectangles_seeing_each_other():
    radiative_surface_manager_instance = RadiativeSurfaceManager.from_random_rectangles_that_see_each_others(
        num_rectangles=num_rectangles,
        min_size=0.1, max_size=10,
        max_distance_factor=10,
        parallel_coaxial_squares=False
    )
    return radiative_surface_manager_instance


class TestRadiativeSurfaceManagerInit:
    """
    Tests for basic functionalities of the RadiativeSurfaceManager class.
    """

    def test_init_radiative_surface_manager(self):
        """
        Test the initialization of the RadiativeSurfaceManager class.
        """
        radiative_surface_manager = RadiativeSurfaceManager()
        assert radiative_surface_manager._radiative_surface_dict == {}
        assert radiative_surface_manager.context_octree is None
        assert radiative_surface_manager._radiance_argument_list == []

    @pytest.mark.parametrize('radiative_surface_instance', [3], indirect=True)
    def test_add_radiative_surface(self, radiative_surface_manager_instance, radiative_surface_instance):
        """
        Test the add_radiative_surface method of the RadiativeSurfaceManager class.
        """
        radiative_surface_list = radiative_surface_instance
        radiative_surface_manager_instance.add_radiative_surfaces(radiative_surface_list)
        for radiative_surface in radiative_surface_list:
            assert radiative_surface.identifier in radiative_surface_manager_instance.get_list_of_radiative_surface_id()

    def test_init_radiative_surface_manager_with_random_rectangles(
            self,
            radiative_surface_manager_instance_with_random_rectangles
    ):
        """
        Test the initialization of the RadiativeSurfaceManager class with random rectangles.
        """
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        assert len(
            radiative_surface_manager.get_list_of_radiative_surface_id()) == num_random_rectangle * num_ref_rectangles + num_ref_rectangles
        for identifier, radiative_surface in radiative_surface_manager._radiative_surface_dict.items():
            assert radiative_surface.identifier == identifier
            if identifier.startswith("ref"):
                assert len(radiative_surface.viewed_surfaces_id_list) == num_random_rectangle

    def test_check_all_viewed_surfaces_in_manager(self,
                                                  radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the check_all_viewed_surfaces_in_manager method of the RadiativeSurfaceManager class.
        """
        # Check the viewed surfaces for the automatically generated radiative surfaces
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        radiative_surface_manager.check_all_viewed_surfaces_in_manager()
        # Add an unknown surface to the viewed surfaces and check the error
        radiative_surface_manager.get_radiative_surface(
            radiative_surface_manager.get_list_of_radiative_surface_id()[0]).add_viewed_surfaces(
            ["unknown_surface"])
        with pytest.raises(ValueError):
            radiative_surface_manager.check_all_viewed_surfaces_in_manager()