"""
Test functions for the RadiativeSurface class.
"""
import os
import pytest

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import time

from src.radiance_comp_vf import RadiativeSurface
from src.radiance_comp_vf import RadiativeSurfaceManager
from src.radiance_comp_vf.utils import split_into_batches
from src.radiance_comp_vf.radiative_surface.radiative_surface_manager_class import flatten_table_to_lists

from .radiative_surface_test import radiative_surface_instance

test_file_dir = os.path.dirname(os.path.abspath(__file__))

radiance_test_file_dir = os.path.join(test_file_dir, "radiance_test_files")


@pytest.fixture(scope='function')
def radiative_surface_manager_instance():
    radiative_surface_manager_instance = RadiativeSurfaceManager()
    return radiative_surface_manager_instance


num_ref_rectangles = 10
num_random_rectangle = 10


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
def radiative_surface_manager_instance_with_random_rectangles():
    radiative_surface_manager_instance = RadiativeSurfaceManager.from_random_rectangles(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=0.1, max_size=10,
        max_distance_factor=10,
        parallel_coaxial_squares=False
    )
    return radiative_surface_manager_instance


class TestRadiativeSurfaceManagerBasic:
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


class TestRadiativeSurfaceManagerRadianceIndividualInputGeneration:

    @staticmethod
    def get_radiative_surface_with_viewed_surfaces(radiative_surface_manager):
        radiative_surface_id_list = radiative_surface_manager.get_list_of_radiative_surface_id()
        for radiative_surface_id in radiative_surface_id_list:
            radiative_surface_obj = radiative_surface_manager.get_radiative_surface(radiative_surface_id)
            if len(radiative_surface_obj.get_viewed_surfaces_id_list()) > 0:
                return radiative_surface_obj

        raise ValueError("No radiative surface with viewed surfaces found.")

    @staticmethod
    def init_folder(radiative_surface_manager):
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = radiative_surface_manager.create_vf_simulation_folders(
            path_root_simulation_folder=radiance_test_file_dir, return_file_path_only=False)
        return path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder

    def test_generate_octree_file(self, radiative_surface_manager_instance_with_random_rectangles):
        """
        Test the generate_emitter_file method of the RadiativeSurfaceManager class.
        """
        radiative_surface_manager = radiative_surface_manager_instance_with_random_rectangles
        # Inititialize the simulation folder
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = self.init_folder(
            radiative_surface_manager)
        # Get the first radiative surface with viewed surfaces
        radiative_surface_obj = self.get_radiative_surface_with_viewed_surfaces(radiative_surface_manager)
        # Get the names of the Radiance files
        name_emitter_rad_file, name_octree_file, name_receiver_rad_file, name_output_file = radiative_surface_obj.generate_rad_file_name()
        # get the radiative surface strings
        receiver_rad_str_list = [radiative_surface_manager.get_radiative_surface(receiver_id).rad_file_content
                                 for
                                 receiver_id in
                                 radiative_surface_obj.get_viewed_surfaces_id_list()]
        # Generate the octree file with 1 batch
        path_octree_file = radiative_surface_manager.generate_octree(
            receiver_rad_str_list=receiver_rad_str_list,
            path_octree_folder=path_octree_folder,
            name_octree_file=name_octree_file,
            num_receiver_per_octree=1000)  # 1000 far beyong the number of viewed surfaces
        # Generate the octree file with more than 1 batch
        path_octree_file = radiative_surface_manager.generate_octree(
            receiver_rad_str_list=receiver_rad_str_list,
            path_octree_folder=path_octree_folder,
            name_octree_file=name_octree_file,
            num_receiver_per_octree=5)


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


class TestRadiativeSurfaceManagerRadianceVFComputation:
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
        radiative_surface_manager.run_vf_computation(
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
        radiative_surface_manager.run_vf_computation_in_parallel(
            nb_rays=nb_rays,
            num_workers=num_workers,
            worker_batch_size=worker_batch_size,
            executor_type=ThreadPoolExecutor
        )
        # Check the output files
        assert len(os.listdir(path_output_folder)) == len(radiative_surface_manager._radiance_argument_list)
        assert len(os.listdir(path_output_folder)) == len(os.listdir(path_receiver_folder))

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
        radiative_surface_manager.run_vf_computation_in_parallel(
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
        radiative_surface_manager.run_vf_computation_in_parallel(
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
        radiative_surface_manager.run_vf_computation_in_parallel(
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
        radiative_surface_manager.run_vf_computation_in_parallel(
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
        # Computation with hole
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
        radiative_surface_manager.run_vf_computation_in_parallel(
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
        # Computation of the hole itself
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
        radiative_surface_manager.run_vf_computation_in_parallel(
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


def test_flatten_table_to_lists():
    """
    Test the flatten_table_to_lists function.
    """
    table = [[[1, 2, 3], [4, 5, 6]], [[]], [7, 8, 9]]
    result = flatten_table_to_lists(table)
    assert result == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]


#########################################
# Parallelization within class
#########################################

# def test_visibility():
#     radiative_surface_manager = RadiativeSurfaceManager.from_random_rectangles(
#         num_ref_rectangles=1,
#         num_random_rectangle=100,
#         min_size=0.1, max_size=10,
#         max_distance_factor=10,
#         parallel_coaxial_squares=False
#     )
#
#     print("")
#     start = time()
#     pyvista_polydata_mesh = radiative_surface_manager.make_pyvista_polydata_mesh_out_of_all_surfaces()
#     print(f"Pyvista mesh creation took: {time() - start:.2f} seconds")
#
#     # Sequential
#     start = time()
#     radiative_surface_manager.get_radiative_surface("ref_0").are_other_surfaces_visible_sequential(
#         radiative_surface_list=[surface for surface in
#                                 radiative_surface_manager._radiative_surface_dict.values() if
#                                 surface.identifier != "ref_0"],
#         context_pyvista_polydata_mesh=pyvista_polydata_mesh)
#     print(f"Sequential took: {time() - start:.2f} seconds")
#
#     # Multithreading
#     start = time()
#     radiative_surface_manager.get_radiative_surface("ref_0").are_other_surfaces_visible(
#         radiative_surface_list=[surface for surface in
#                                 radiative_surface_manager._radiative_surface_dict.values() if
#                                 surface.identifier != "ref_0"],
#         context_pyvista_polydata_mesh=pyvista_polydata_mesh,
#         executor_type=ThreadPoolExecutor,
#         num_workers=4,
#         worker_batch_size=10)
#     print(f"Multithreading took: {time() - start:.2f} seconds")
#     # Multiprocessing
#     start = time()
#     radiative_surface_manager.get_radiative_surface("ref_0").are_other_surfaces_visible(
#         radiative_surface_list=[surface for surface in
#                                 radiative_surface_manager._radiative_surface_dict.values() if
#                                 surface.identifier != "ref_0"],
#         context_pyvista_polydata_mesh=pyvista_polydata_mesh,
#         executor_type=ProcessPoolExecutor,
#         num_workers=4,
#         worker_batch_size=10)
#     print(f"Multithreading took: {time() - start:.2f} seconds")


def test_visibility():
    num_random_rectangle = 100
    num_ref_rectangles = 1
    radiative_surface_manager = RadiativeSurfaceManager.from_random_rectangles(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=1, max_size=1,
        max_distance_factor=50,
        parallel_coaxial_squares=False
    )

    # sequential
    start= time()
    radiative_surface_manager.check_surface_visibility_sequential(mvfc=0.00001)
    print(f"Sequential took: {time() - start:.2f} seconds")

    start = time()
    radiative_surface_manager.check_surface_visibility(mvfc=0.00001, num_workers=16)
    print(f"Multithreading took: {time() - start:.2f} seconds")