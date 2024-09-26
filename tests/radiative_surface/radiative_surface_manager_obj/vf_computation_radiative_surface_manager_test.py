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
from .radiance_file_generation_radiative_surface_manager_test import radiance_test_file_dir


class TestRadiativeSurfaceManagerRadianceVFComputationNormalCases:
    """
    Tests for the computation of view factors by the RadiativeSurfaceManager class with Radiance.
    """

    def test_run_vf_computation(self, radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the compute_view_factors method of the RadiativeSurfaceManager class.
        """
        # Initialize the radiative surface manager and folders
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # File generation
        num_receiver_per_file = 5
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=4,
            worker_batch_size=10,
            executor_type=ThreadPoolExecutor
        )
        # Check the number of files
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=True)
        assert len(os.listdir(path_receiver_folder)) == len(radiative_surface_manager._radiance_argument_list)
        # Compute the view factors
        nb_rays = 10000
        radiative_surface_manager._run_radiance_vf_computation_sequential(
            nb_rays=nb_rays
        )
        # Check the output files
        assert len(os.listdir(path_output_folder)) == len(radiative_surface_manager._radiance_argument_list)
        assert len(os.listdir(path_output_folder)) == len(os.listdir(path_receiver_folder))

    def test_run_vf_computation_in_parallel(self, radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the compute_view_factors method of the RadiativeSurfaceManager class.
        """
        # Initialize the radiative surface manager and folders
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # File generation
        num_receiver_per_file = 5
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=4,
            worker_batch_size=10,
            executor_type=ThreadPoolExecutor
        )
        # Check the number of files
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=True)
        assert len(os.listdir(path_receiver_folder)) == len(radiative_surface_manager._radiance_argument_list)
        # Compute the view factors
        nb_rays = 10000
        num_workers = 8
        worker_batch_size = 2
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        # Check the output files
        assert len(os.listdir(path_output_folder)) == len(radiative_surface_manager._radiance_argument_list)
        assert len(os.listdir(path_output_folder)) == len(os.listdir(path_receiver_folder))

    def test_run_vf_computation_in_parallel_without_output(self,
                                                           radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the compute_view_factors method of the RadiativeSurfaceManager class.
        """
        # Initialize the radiative surface manager and folders
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # File generation
        num_receiver_per_file = 5
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=4,
            worker_batch_size=10,
            executor_type=ThreadPoolExecutor
        )
        # Check the number of files
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=True)
        assert len(os.listdir(path_receiver_folder)) == len(radiative_surface_manager._radiance_argument_list)
        # Compute the view factors
        nb_rays = 10000
        num_workers = 2
        worker_batch_size = 1
        # file generated
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        # No files
        result = radiative_surface_manager._run_radiance_vf_computation_in_parallel_without_output_files(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ProcessPoolExecutor
        )

        print(result)

class TestRadiativeSurfaceManagerRadianceVFComputationSurfacesWithHoles:

    def test_run_vf_computation_with_surfaces_with_holes(self):
        surface_0 = [
            [0., 0., 0.],
            [10., 0., 0.],
            [10., 10., 0.],
            [0., 10., 0.]
        ]
        surface_1 = [
            [0., 0., 10.],
            [0., 10., 10.],
            [10., 10., 10.],
            [10., 0., 10.]
        ]
        hole_0_sur_1 = [
            [4., 4., 10.],
            [4., 6., 10.],
            [6., 6., 10.],
            [6., 4., 10.]
        ]
        num_receiver_per_file = 1
        nb_rays = 100000
        num_workers = 1
        worker_batch_size = 1
        # ---------------------------------------------------------
        # Computation without hole
        # ---------------------------------------------------------
        radiative_surface_manager = RadiativeSurfaceManager()
        radiative_surface_obj_0 = RadiativeSurface.from_vertex_list(vertex_list=surface_0,
                                                                    identifier="surface_0")
        radiative_surface_obj_1 = RadiativeSurface.from_vertex_list(vertex_list=surface_1,
                                                                    identifier="surface_1")
        radiative_surface_obj_0.add_viewed_surfaces(["surface_1"])
        radiative_surface_manager.add_radiative_surfaces([radiative_surface_obj_0, radiative_surface_obj_1])
        # file generation
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        # Compute the view factors
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        radiative_surface_manager.read_vf_from_radiance_output_files(
            path_output_folder=radiance_test_file_dir)
        vf_witout_hole = \
            radiative_surface_manager.get_radiative_surface("surface_0").viewed_surfaces_view_factor_list[0]
        # ---------------------------------------------------------
        # Computation with hole
        # ---------------------------------------------------------
        radiative_surface_manager = RadiativeSurfaceManager()
        radiative_surface_obj_0 = RadiativeSurface.from_vertex_list(vertex_list=surface_0,
                                                                    identifier="surface_0")
        radiative_surface_obj_1_with_holes = RadiativeSurface.from_vertex_list(vertex_list=surface_1,
                                                                               identifier="surface_1_with_hole",
                                                                               hole_list=[hole_0_sur_1])
        radiative_surface_obj_0.add_viewed_surfaces(["surface_1_with_hole"])
        radiative_surface_manager.add_radiative_surfaces(
            [radiative_surface_obj_0, radiative_surface_obj_1_with_holes])
        # file generation
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        # Compute the view factors
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        radiative_surface_manager.read_vf_from_radiance_output_files(
            path_output_folder=radiance_test_file_dir)
        vf_with_hole = \
            radiative_surface_manager.get_radiative_surface("surface_0").viewed_surfaces_view_factor_list[0]

        # ---------------------------------------------------------
        # Computation of the hole itself
        # ---------------------------------------------------------
        radiative_surface_manager = RadiativeSurfaceManager()
        radiative_surface_obj_0 = RadiativeSurface.from_vertex_list(vertex_list=surface_0,
                                                                    identifier="surface_0")
        radiative_hole_obj = RadiativeSurface.from_vertex_list(vertex_list=hole_0_sur_1,
                                                               identifier="hole_0_sur_1")

        radiative_surface_obj_0.add_viewed_surfaces(["hole_0_sur_1"])
        radiative_surface_manager.add_radiative_surfaces(
            [radiative_surface_obj_0, radiative_hole_obj])
        # file generation
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=num_receiver_per_file,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        # Compute the view factors
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        radiative_surface_manager.read_vf_from_radiance_output_files(
            path_output_folder=radiance_test_file_dir)
        vf_hole = \
            radiative_surface_manager.get_radiative_surface("surface_0").viewed_surfaces_view_factor_list[0]

        print("")
        print(f"vf_witout_hole: {vf_witout_hole}")
        print(f"vf with hole: {vf_with_hole}")
        print(f"vf hole: {vf_hole}")
        print(f"vf_with_hole/(vf_witout_hole-vf_hole): {vf_with_hole / (vf_witout_hole - vf_hole)}")
        assert abs(1 - vf_with_hole / (vf_witout_hole - vf_hole)) < 0.02  # Error margin of 2%

class TestRadiativeSurfaceManagerRadianceVFComputationObstructionInOctree:
    """
    todo: check if up to date and update if necessary
    """
    def test_run_vf_computation_with_obstruction_in_octree(self):


        surface_0 = [
            [0., 0., 0.],
            [10., 0., 0.],
            [10., 10., 0.],
            [0., 10., 0.]
        ]
        surface_1 = [
            [4., 4., 5.],
            [4., 6., 5.],
            [6., 6., 5.],
            [6., 4., 5.]
        ]
        surface_2 = [
            [0., 0., 10.],
            [0., 10., 10.],
            [10., 10., 10.],
            [10., 0., 10.]
        ]

        nb_rays = 1000000

        # ---------------------------------------------------------
        # Computation Surface 1
        # ---------------------------------------------------------
        radiative_surface_manager = RadiativeSurfaceManager()
        radiative_surface_obj_0 = RadiativeSurface.from_vertex_list(vertex_list=surface_0,
                                                                    identifier="surface_0")
        radiative_surface_obj_1 = RadiativeSurface.from_vertex_list(vertex_list=surface_1,
                                                                    identifier="surface_1")
        radiative_surface_obj_0.add_viewed_surfaces(["surface_1"])
        radiative_surface_manager.add_radiative_surfaces([radiative_surface_obj_0, radiative_surface_obj_1])
        # file generation
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=1,
            num_workers=1,
            worker_batch_size=1,
            executor_type=ThreadPoolExecutor
        )
        # Compute the view factors
        num_workers = 1
        worker_batch_size = 1
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        radiative_surface_manager.read_vf_from_radiance_output_files(
            path_output_folder=radiance_test_file_dir)
        vf_s1 = radiative_surface_manager.get_radiative_surface("surface_0").viewed_surfaces_view_factor_list[
            0]
        # ---------------------------------------------------------
        # Computation surface 2
        # ---------------------------------------------------------
        radiative_surface_manager = RadiativeSurfaceManager()
        radiative_surface_obj_0 = RadiativeSurface.from_vertex_list(vertex_list=surface_0,
                                                                    identifier="surface_0")
        radiative_surface_obj_2 = RadiativeSurface.from_vertex_list(vertex_list=surface_2,
                                                                    identifier="surface_2")
        radiative_surface_obj_0.add_viewed_surfaces(["surface_2"])
        radiative_surface_manager.add_radiative_surfaces([radiative_surface_obj_0, radiative_surface_obj_2])
        # file generation
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=1,
            num_workers=1,
            worker_batch_size=1,
            executor_type=ThreadPoolExecutor
        )
        # Compute the view factors
        num_workers = 1
        worker_batch_size = 1
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        radiative_surface_manager.read_vf_from_radiance_output_files(
            path_output_folder=radiance_test_file_dir)
        vf_s2 = \
            radiative_surface_manager.get_radiative_surface("surface_0").viewed_surfaces_view_factor_list[0]

        # ---------------------------------------------------------
        # Computation with both surfaces
        # ---------------------------------------------------------
        radiative_surface_manager = RadiativeSurfaceManager()
        radiative_surface_obj_0 = RadiativeSurface.from_vertex_list(vertex_list=surface_0,
                                                                    identifier="surface_0")
        radiative_surface_obj_1 = RadiativeSurface.from_vertex_list(vertex_list=surface_1,
                                                                    identifier="surface_1")
        radiative_surface_obj_2 = RadiativeSurface.from_vertex_list(vertex_list=surface_2,
                                                                    identifier="surface_2")
        radiative_surface_obj_0.add_viewed_surfaces(["surface_1", "surface_2"])
        radiative_surface_manager.add_radiative_surfaces(
            [radiative_surface_obj_0, radiative_surface_obj_1, radiative_surface_obj_2])
        # file generation
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=1,
            num_workers=1,
            worker_batch_size=1,
            executor_type=ThreadPoolExecutor
        )
        # Compute the view factors
        num_workers = 1
        worker_batch_size = 1
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        radiative_surface_manager.read_vf_from_radiance_output_files(
            path_output_folder=radiance_test_file_dir)
        [vf_s1_obs, vf_s2_obs] = radiative_surface_manager.get_radiative_surface(
            "surface_0").viewed_surfaces_view_factor_list

        print("")
        print(f"vf_s1: {vf_s1}")
        print(f"vf_s2: {vf_s2}")
        print(f"vf_s1_obs: {vf_s1_obs}")
        print(f"vf_s2_obs: {vf_s2_obs}")
        print(f"(1-vf_s2_obs/(vf_s2-vf_s1))*100: {(1 - vf_s2_obs / (vf_s2 - vf_s1)) * 100}")

        # ---------------------------------------------------------
        # Computation with both surfaces one octree
        # ---------------------------------------------------------
        radiative_surface_manager = RadiativeSurfaceManager()
        radiative_surface_obj_0 = RadiativeSurface.from_vertex_list(vertex_list=surface_0,
                                                                    identifier="surface_0")
        radiative_surface_obj_1 = RadiativeSurface.from_vertex_list(vertex_list=surface_1,
                                                                    identifier="surface_1")
        radiative_surface_obj_2 = RadiativeSurface.from_vertex_list(vertex_list=surface_2,
                                                                    identifier="surface_2")
        radiative_surface_obj_0.add_viewed_surfaces(["surface_1", "surface_2"])
        radiative_surface_manager.add_radiative_surfaces(
            [radiative_surface_obj_0, radiative_surface_obj_1, radiative_surface_obj_2])
        # file generation
        radiative_surface_manager.generate_radiance_inputs_for_all_surfaces_in_parallel(
            path_root_simulation_folder=radiance_test_file_dir,
            num_receiver_per_file=1,
            num_workers=1,
            worker_batch_size=1,
            executor_type=ThreadPoolExecutor,
            one_octree_for_all=True
        )
        # Compute the view factors
        num_workers = 1
        worker_batch_size = 1
        radiative_surface_manager._run_radiance_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        radiative_surface_manager.read_vf_from_radiance_output_files(
            path_output_folder=radiance_test_file_dir)
        [vf_s1_obs_one_octree, vf_s2_obs_one_octree] = radiative_surface_manager.get_radiative_surface(
            "surface_0").viewed_surfaces_view_factor_list

        print("")
        print(f"vf_s1_obs_one_octree: {vf_s1_obs_one_octree}")
        print(f"vf_s2_obs_one_octree: {vf_s2_obs_one_octree}")


def test_flatten_table_to_lists():
    """
    Test the flatten_table_to_lists function.
    """
    table = [[[1, 2, 3], [4, 5, 6]], [[]], [7, 8, 9]]
    result = flatten_table_to_lists(table)
    assert result == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
