"""
Test functions for the Radiance input files generation for the RadiativeSurfaceManager class.
"""
import os
import pytest

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import time

from src.radiance_comp_vf import RadiativeSurface
from src.radiance_comp_vf import RadiativeSurfaceManager
from src.radiance_comp_vf.radiative_surface.radiative_surface_manager_class import flatten_table_to_lists

from tests.radiative_surface.radiative_surface_obj.radiative_surface_test import radiative_surface_instance
from .init_radiative_surface_manager_test import \
    radiative_surface_manager_instance_with_random_rectangles_seeing_each_other, \
    radiative_surface_manager_instance_with_random_rectangles

test_file_dir = os.path.dirname(os.path.abspath(__file__))

radiance_test_file_dir = os.path.join(os.path.dirname(test_file_dir), "radiance_test_files")





class TestRadiativeSurfaceManagerRadianceInputGeneration:
    """
    Tests for the generation of Radiance input files by the RadiativeSurfaceManager class.
    """

    def test_generate_radiance_files_in_parallel(self,
                                                 radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the generate_radiance_files method of the RadiativeSurfaceManager class.
        """
        # Initialize the radiative surface manager and folders
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # Generate the files
        num_receiver_per_file = 5
        num_workers = 4
        worker_batch_size = 10
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        # Check the number of files
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=True)
        num_emitter = len(
            [identifier for identifier, rad_surface_obj in
             radiative_surface_manager._radiative_surface_dict.items() if
             len(rad_surface_obj.viewed_surfaces_id_list) > 0])
        num_emitter_files = len(os.listdir(path_emitter_folder))
        assert num_emitter == num_emitter_files
        assert len(os.listdir(path_receiver_folder)) == len(radiative_surface_manager._radiance_argument_list)

class TestRadiativeSurfaceManagerRadianceInputGenerationCheckOctreeOptions:
    """
    Tests for the generation of Radiance input files by the RadiativeSurfaceManager class.
    """

    def test_generate_radiance_files_in_parallel_without_octree(self,
                                                 radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the generate_radiance_files method of the RadiativeSurfaceManager class.
        """
        # Initialize the radiative surface manager and folders
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # Generate the files
        num_receiver_per_file = 5
        num_workers = 4
        worker_batch_size = 10
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor,
            consider_octree=False
        )
        # Check the number of files
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=True)
        num_emitter = len(
            [identifier for identifier, rad_surface_obj in
             radiative_surface_manager._radiative_surface_dict.items() if
             len(rad_surface_obj.viewed_surfaces_id_list) > 0])
        num_emitter_files = len(os.listdir(path_emitter_folder))
        assert num_emitter == num_emitter_files
        assert len(os.listdir(path_receiver_folder)) == len(radiative_surface_manager._radiance_argument_list)
        assert len(os.listdir(path_octree_folder)) == 0
        # print (path_octree_folder)

    def test_generate_radiance_files_in_parallel_with_one_octree(self,
                                                 radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the generate_radiance_files method of the RadiativeSurfaceManager class.
        """
        # Initialize the radiative surface manager and folders
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # Generate the files
        num_receiver_per_file = 5
        num_workers = 4
        worker_batch_size = 10
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor,
            consider_octree=True,
            one_octree_for_all=True
        )
        # Check the number of files
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=True)
        num_emitter = len(
            [identifier for identifier, rad_surface_obj in
             radiative_surface_manager._radiative_surface_dict.items() if
             len(rad_surface_obj.viewed_surfaces_id_list) > 0])
        num_emitter_files = len(os.listdir(path_emitter_folder))
        assert num_emitter == num_emitter_files
        assert len(os.listdir(path_receiver_folder)) == len(radiative_surface_manager._radiance_argument_list)
        assert len(os.listdir(path_octree_folder)) == 2 # one octree file and one rad file
        # print (path_octree_folder)

# todo: add test for cases that should return errors (and check with and without octree etc)