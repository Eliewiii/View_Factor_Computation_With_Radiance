
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
from .radiance_file_generation_radiative_surface_manager_test import radiance_test_file_dir




class TestRadiativeSurfaceManagerMatrixGeneration:

    @staticmethod
    def make_input_files_for_radiance_vf_computation(radiative_surface_manager, num_receiver_per_file) -> [str, str,
                                                                                                           str, str]:
        """
        Generate the Radiance input files for the view factor computation.
        """
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=0,
            worker_batch_size=10,
            executor_type=ThreadPoolExecutor
        )
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=True)
        return path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder
    def test_generate_matrices(self,radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the compute_view_factors method of the RadiativeSurfaceManager class.
        """
        # Initialize the radiative surface manager and folders
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # File generation
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = self.make_input_files_for_radiance_vf_computation(
            radiative_surface_manager, num_receiver_per_file=5)
        # Compute the view factors
        nb_rays = 1000000
        num_workers = 2
        worker_batch_size = 1
        # No files
        radiative_surface_manager._run_radiance_vf_computation_in_parallel_without_output_files(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )
        # generate view factor matrix
        f_mtx = radiative_surface_manager._generate_view_factor_matrix()
        assert f_mtx.shape == (radiative_surface_manager.num_surface, radiative_surface_manager.num_surface)
        print ("\n", f_mtx)
        # # generate emissivity matrix
        # e_mtx = radiative_surface_manager._generate_emissivity_matrix()
        # assert e_mtx.shape == (radiative_surface_manager.num_surface, radiative_surface_manager.num_surface)
        # print ("\n", e_mtx)
        # # generate reflectivity matrix
        # r_mtx = radiative_surface_manager._generate_reflectivity_matrix()
        # assert r_mtx.shape == (radiative_surface_manager.num_surface, radiative_surface_manager.num_surface)
        # print ("\n", r_mtx)
        # # generate matrix of the surface areas
        # a_mtx = radiative_surface_manager._generate_area_matrix()
        # assert a_mtx.shape == (radiative_surface_manager.num_surface, radiative_surface_manager.num_surface)
        # print ("\n", a_mtx)

































