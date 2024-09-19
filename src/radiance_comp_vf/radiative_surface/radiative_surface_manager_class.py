"""
Class that manages the whole LWR simulation, especially the RadiativeSurface objects.
"""

import os
import pickle
import warnings

from typing import List
from copy import deepcopy

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from pyvista import PolyData

from .radiative_surface_class import RadiativeSurface

from ..utils import from_receiver_rad_str_to_rad_files, from_receiver_rad_str_to_octree_file, \
    from_emitter_rad_str_to_rad_file, split_into_batches, \
    create_folder, parallel_computation_in_batches_with_return, run_radiant_vf_computation_in_batches, \
    compute_vf_between_emitter_and_receivers_radiance, generate_random_rectangles, object_method_wrapper


class RadiativeSurfaceManager:
    """
    Class that manages the whole RadiativeSurface objects.
    """
    # Parameters for the workers for parallel computation
    DEFAULT_WORKER_CPU_BOUND = os.cpu_count()
    DEFAULT_WORKER_IO_BOUND = os.cpu_count() * 2
    CPU_BOUND_LIMIT_MULTIPLIER = 1.5
    IO_BOUND_LIMIT_MULTIPLIER = 3
    MAX_WORKER_CPU_BOUND = os.cpu_count() * CPU_BOUND_LIMIT_MULTIPLIER
    MAX_WORKER_IO_BOUND = os.cpu_count() * IO_BOUND_LIMIT_MULTIPLIER

    def __init__(self):
        self._radiative_surface_dict: dict = {}
        self._radiance_argument_list: List[List] = []
        # Simulation parameters
        self._sim_parameter_dict = {"num_rays": None, "num_receiver_per_file": None}

    def __str__(self):
        return (f"RadiativeSurfaceManager with {len(self._radiative_surface_dict)} RadiativeSurface objects."
                f"list of RadiativeSurface objects: {list(self._radiative_surface_dict.keys())}")

    ##################################
    # Initialization with Class Methods
    ##################################

    @classmethod
    def from_random_rectangles(cls, num_ref_rectangles: int = 1, num_random_rectangle: int = 10,
                               min_size: float = 0.01, max_size: float = 10,
                               max_distance_factor: float = 10,
                               parallel_coaxial_squares: bool = False) -> "RadiativeSurfaceManager":
        """
        Make a RadiativeSurfaceManager object from random rectangles PolyData.
        Random rectangles are generated by pairs of 1 reference rectangle (normalized) and num_random_rectangle random
        rectangles.
        The reference rectangles see their associated random rectangles.
        The random rectangle do not see each any surfaces, thus no view factor computation will be performed on them.
        :param num_ref_rectangles: int, the number of reference rectangles generated.
        :param num_random_rectangle: int, the number of random rectangles generated per reference rectangles.
        :param min_size: float, the minimum size of the rectangles. The reference rectangles being normalized with one
            edge size equal to 1.
        :param max_size: float, the maximum size of the rectangles. The reference rectangles being normalized with one
            edge size equal to 1.
        :param max_distance_factor: float, the maximum distance factor between the reference and random rectangles. The
            maximum distance being max_distance_factor * max_size.
        :param parallel_coaxial_squares: bool, if True, the random rectangles are generated parallel and coaxial to the
            reference rectangles.
        :return: RadiativeSurfaceManager, the RadiativeSurfaceManager object.
        """
        radiative_surface_manager = cls()
        # Generate the random rectangles PolyData
        for i in range(num_ref_rectangles):
            ref_rectangles, random_rectangle_list = generate_random_rectangles(
                nb_random_rectangles=num_random_rectangle, min_size=min_size, max_size=max_size,
                max_distance_factor=max_distance_factor,
                parallel_coaxial_squares=parallel_coaxial_squares)
            # Set the id
            id_ref = f"ref_{i}"
            id_random_list = [f"random_{j}_ref_{i}" for j in range(num_random_rectangle)]
            # Convert the PolyData to RadiativeSurface objects
            ref_rad_surface_obj = RadiativeSurface.from_polydata(identifier=id_ref, polydata=ref_rectangles)
            random_rad_surface_obj_list = [
                RadiativeSurface.from_polydata(identifier=id_random, polydata=random_rectangle)
                for id_random, random_rectangle in zip(id_random_list, random_rectangle_list)]
            ref_rad_surface_obj.add_viewed_surfaces(id_random_list)
            # Add the RadiativeSurface objects to the manager
            radiative_surface_manager.add_radiative_surfaces(ref_rad_surface_obj, random_rad_surface_obj_list,
                                                             check_id_uniqueness=True)

        return radiative_surface_manager

    @classmethod
    def from_random_rectangles_that_see_each_others(cls, num_rectangles: int = 2,
                                                    min_size: float = 0.01, max_size: float = 10,
                                                    max_distance_factor: float = 10,
                                                    parallel_coaxial_squares: bool = False) -> "RadiativeSurfaceManager":
        """
        Make a RadiativeSurfaceManager object from random rectangles PolyData.
        Random rectangles are generated by pairs of 1 reference rectangle (normalized) and num_random_rectangle random
        rectangles.
        The reference rectangles see their associated random rectangles.
        The random rectangle do not see each any surfaces, thus no view factor computation will be performed on them.
        :param num_rectangles: int, the number of rectangles generated.
        :param min_size: float, the minimum size of the rectangles. The reference rectangles being normalized with one
            edge size equal to 1.
        :param max_size: float, the maximum size of the rectangles. The reference rectangles being normalized with one
            edge size equal to 1.
        :param max_distance_factor: float, the maximum distance factor between the reference and random rectangles. The
            maximum distance being max_distance_factor * max_size.
        :param parallel_coaxial_squares: bool, if True, the random rectangles are generated parallel and coaxial to the
            reference rectangles.
        :return: RadiativeSurfaceManager, the RadiativeSurfaceManager object.
        """
        if num_rectangles < 2:
            raise ValueError("The number of rectangles must be at least 2.")
        radiative_surface_manager = cls()
        # Generate the random rectangles PolyData
        ref_rectangles, random_rectangle_list = generate_random_rectangles(
            nb_random_rectangles=num_rectangles - 1, min_size=min_size, max_size=max_size,
            max_distance_factor=max_distance_factor,
            parallel_coaxial_squares=parallel_coaxial_squares)
        # Set the id
        id_ref = f"rect_{0}"
        id_random_list = [f"rect_{i}" for i in range(1, num_rectangles)]
        # Convert the PolyData to RadiativeSurface objects
        ref_rad_surface_obj = RadiativeSurface.from_polydata(identifier=id_ref, polydata=ref_rectangles)
        ref_rad_surface_obj.add_viewed_surfaces(id_random_list)

        random_rad_surface_obj_list = [
            RadiativeSurface.from_polydata(identifier=id_random, polydata=random_rectangle)
            for id_random, random_rectangle in zip(id_random_list, random_rectangle_list)]
        for random_rad_surface_obj in random_rad_surface_obj_list:
            for identifier in id_random_list + [id_ref]:
                if identifier != random_rad_surface_obj.identifier:
                    random_rad_surface_obj.add_viewed_surfaces([identifier])

        # Add the RadiativeSurface objects to the manager
        radiative_surface_manager.add_radiative_surfaces(ref_rad_surface_obj, random_rad_surface_obj_list,
                                                         check_id_uniqueness=True)

        return radiative_surface_manager

    # ----------------------------------------------------------
    # Core Functions
    # ----------------------------------------------------------

    def to_pkl(self, path_folder: str, file_name: str = "radiative_surface_manager.pkl"):
        """
        Save the RadiativeSurfaceManager object to a pickle file.
        :param path_folder: str, the folder path where the pickle file will be saved.
        :param file_name: str, the name of the pickle file.
        """

        path_pkl_file = os.path.join(path_folder, file_name)
        with open(path_pkl_file, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def from_pkl(cls, path_pkl_file) -> "RadiativeSurfaceManager":
        """
        Load a RadiativeSurfaceManager object from a pickle file.
        :param path_pkl_file: str, the path of the pickle file.
        :return: RadiativeSurfaceManager, the RadiativeSurfaceManager object.
        """
        with open(path_pkl_file, 'rb') as f:
            radiative_surface_manager = pickle.load(f)
        return radiative_surface_manager

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------
    @property
    def sim_parameter_dict(self):
        return deepcopy(self._sim_parameter_dict)

    # -----------------------------------------------------------------
    # Add surfaces
    # -----------------------------------------------------------------

    def add_radiative_surfaces(self, *args, check_id_uniqueness=True):
        """
        Add multiple RadiativeSurface objects to the manager.
        The arguments can be either RadiativeSurface or list of RadiativeSurface.
        :param args: RadiativeSurface or [RadiativeSurface], the RadiativeSurface objects to add.
        :param check_id_uniqueness: bool, if True, check if the id of the RadiativeSurface object is unique.
        """
        for radiative_surface_element_or_list in args:
            if isinstance(radiative_surface_element_or_list, list):
                for radiative_surface_obj in radiative_surface_element_or_list:
                    self.add_radiative_surface(radiative_surface_obj, check_id_uniqueness)
            elif isinstance(radiative_surface_element_or_list, RadiativeSurface):
                self.add_radiative_surface(radiative_surface_element_or_list, check_id_uniqueness)
            else:
                raise ValueError(
                    "The input object is not a RadiativeSurface object nor a list of RadiativeSurface objects.")

    def add_radiative_surface(self, radiative_surface: RadiativeSurface, check_id_uniqueness=True):
        """
        Add a RadiativeSurface object to the manager.
        :param radiative_surface: RadiativeSurface, the RadiativeSurface object to add.
        :param check_id_uniqueness: bool, if True, check if the id of the RadiativeSurface object is unique.
        """
        if not isinstance(radiative_surface, RadiativeSurface):
            raise ValueError("The input object is not a RadiativeSurface object.")
        if check_id_uniqueness and radiative_surface.identifier in self._radiative_surface_dict:
            raise ValueError(
                f"The RadiativeSurface id {radiative_surface.identifier} object already exists in the surface manager.")
        self._radiative_surface_dict[radiative_surface.identifier] = radiative_surface

    # -----------------------------------------------------------------
    # Access to the surface
    # -----------------------------------------------------------------
    def get_radiative_surface(self, identifier: str) -> RadiativeSurface:
        """
        Get a RadiativeSurface object from the manager.
        :param identifier: str, the identifier of the RadiativeSurface object.
        :return: RadiativeSurface, the RadiativeSurface object.
        """
        if identifier not in self._radiative_surface_dict:
            raise ValueError(
                f"The RadiativeSurface id {identifier} object does not exist in the surface manager.")
        return self._radiative_surface_dict[identifier]

    def get_list_of_radiative_surface_id(self) -> List[str]:
        """
        Get the list of the identifiers of the RadiativeSurface objects in the manager.
        :return:
        """
        return list(self._radiative_surface_dict.keys())

    def _add_argument_to_radiance_argument_list(self, argument_list: List[List[str]]):
        """
        Add an argument to the Radiance argument list.
        :param argument_list: the argument_list to add.
        """
        for argument in argument_list:
            if isinstance(argument, list) and not argument == []:
                self._radiance_argument_list.append(argument)

    def reinitialize_radiance_argument_list(self):
        """
        Reinitialize the Radiance argument list.
        """
        self._radiance_argument_list = []

    def check_all_viewed_surfaces_in_manager(self):
        """
        Check if all the viewed surfaces of the RadiativeSurface objects are in the manager.
        """
        for radiative_surface_obj in self._radiative_surface_dict.values():
            for viewed_surface_id in radiative_surface_obj.viewed_surfaces_id_list:
                if viewed_surface_id not in self._radiative_surface_dict:
                    raise ValueError(
                        f"The viewed surface {viewed_surface_id} of the surface {radiative_surface_obj.identifier} "
                        f"is not in the radiative surface manager.")

    # -----------------------------------------------------------------
    # Visibility check
    # -----------------------------------------------------------------

    def check_surface_visibility(self,
                                 mvfc: float = None,

                                 num_workers: int = 0,
                                 ray_traced_check: bool = True
                                 ):

        """
        Check the visibility between all the RadiativeSurface objects in the manager.
        :param mvfc: float, the minimum visibility factor criterion to consider the surface as visible.
        :param num_workers: int, the number of workers to use for the parallelization.
        """
        # todo: set the chunk size to nb_surface//num_workers, and set num worker to nb thread
        num_workers = self.check_num_worker_valid(num_workers, worker_type="cpu")
        mvfc = self.check_min_vf_criterion(mvfc)


        chunk_size = max(1, len(self._radiative_surface_dict) // num_workers)
        visibility_result_dict_list = parallel_computation_in_batches_with_return(
            func=self._check_visibility_of_surface_chunk,
            input_tables=split_into_batches(list(self._radiative_surface_dict.keys()), chunk_size),
            executor_type=ProcessPoolExecutor,
            worker_batch_size=1,
            num_workers=num_workers,
            radiative_surface_manager_obj=self,
            mvfc=mvfc)

        # todo: redistribute the results to the radiative surface objects

    def check_surface_visibility_sequential(self, mvfc):
        """
        Check the visibility between all the RadiativeSurface objects in the manager.
        todo: remove function eventually
        """
        mesh = self.make_pyvista_polydata_mesh_out_of_all_surfaces()
        visibility_result_dict = {}
        for radiative_surface_obj in self._radiative_surface_dict.values():
            visibility_result_dict[
                radiative_surface_obj.identifier] = radiative_surface_obj.are_other_surfaces_visible(
                radiative_surface_list=self._radiative_surface_dict.values(),
                context_pyvista_polydata_mesh=mesh,
                mvfc=mvfc)

        # print(visibility_result_dict)

    @staticmethod
    def _check_visibility_of_surface_chunk(*radiative_surface_id_list,
                                           radiative_surface_manager_obj: 'RadiativeSurfaceManager', mvfc):
        """

        :param radiative_surface_manager_obj:
        :param chunk_size:
        :return:
        """
        pyvista_polydata_mesh = radiative_surface_manager_obj.make_pyvista_polydata_mesh_out_of_all_surfaces()
        visibility_result_dict = {}
        for radiative_surface_id in radiative_surface_id_list:
            visibility_result_dict[
                radiative_surface_id] = radiative_surface_manager_obj.get_radiative_surface(
                radiative_surface_id).are_other_surfaces_visible(
                radiative_surface_list=radiative_surface_manager_obj._radiative_surface_dict.values(),
                context_pyvista_polydata_mesh=pyvista_polydata_mesh, mvfc=mvfc)
        return visibility_result_dict

    def _make_pyvista_polydata_mesh_out_of_all_surfaces(self):
        """
        Make a PyVista PolyData object out of all the RadiativeSurface objects in the manager.
        """
        mesh = PolyData()
        for radiative_surface_obj in self._radiative_surface_dict.values():
            mesh += radiative_surface_obj.to_pyvista_polydata()
        return mesh

    ###############################
    # Files and commands generation
    ###############################
    def generate_radiance_inputs_for_all_surfaces_in_parallel(self, path_root_simulation_folder: str,
                                                              num_receiver_per_file: int = 1,
                                                              num_workers=1, worker_batch_size=1,
                                                              executor_type=ThreadPoolExecutor,
                                                              overwrite_folders: bool = False,
                                                              num_receiver_per_octree: int = 1000,
                                                              consider_octree: bool = True):
        """
        Generate the Radiance input files for all the RadiativeSurface objects in parallel.
        :param path_root_simulation_folder: str, the folder path where the Radiance files will be saved.
        :param num_receiver_per_file: int, the number of receivers in the receiver rad file per batch.
        :param num_workers: int, the number of workers to use for the parallelization
        :param worker_batch_size: int, the size of the batch of surfaces to process in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        :param overwrite_folders: bool, if True, overwrite the folders if they already exist.
        :param num_receiver_per_octree: int, the number of receivers per octree sub file
            (due to radiance limitation)
        :param consider_octree: bool, if True, consider the octree file in the Radiance command.
        """
        # Generate the folder if they don't exist
        path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder = self.create_vf_simulation_folders(
            path_root_simulation_folder,
            overwrite=overwrite_folders)
        # Run in parallel the generation of the Radiance files
        argument_list_to_add = parallel_computation_in_batches_with_return(
            func=self.generate_radiance_inputs_for_one_surface,
            input_tables=[[radiative_surface_obj] for radiative_surface_obj in
                          self._radiative_surface_dict.values()],
            executor_type=executor_type,
            worker_batch_size=worker_batch_size,
            num_workers=num_workers,
            path_emitter_folder=path_emitter_folder,
            path_octree_folder=path_octree_folder,
            path_receiver_folder=path_receiver_folder,
            path_output_folder=path_output_folder,
            num_receiver_per_file=num_receiver_per_file,
            num_receiver_per_octree=num_receiver_per_octree,
            consider_octree=consider_octree)

        argument_list_to_add = flatten_table_to_lists(argument_list_to_add)

        self._add_argument_to_radiance_argument_list(argument_list_to_add)

    def generate_radiance_inputs_for_one_surface(self, radiative_surface_obj: RadiativeSurface,
                                                 path_emitter_folder: str, path_octree_folder: str,
                                                 path_receiver_folder: str,
                                                 path_output_folder: str, num_receiver_per_file: int = 1,
                                                 num_receiver_per_octree: int = 1000,
                                                 consider_octree: bool = True):
        """
        Generate the Radiance input files for one RadiativeSurface object.
        :param radiative_surface_obj: RadiativeSurface, the RadiativeSurface object.
        :param path_emitter_folder: str, the folder path where the emitter Radiance files will be saved.
        :param path_octree_folder: str, the folder path where the octree files will be saved.
        :param path_receiver_folder: str, the folder path where the receiver Radiance files will be saved.
        :param path_output_folder: str, the folder path where the output Radiance files will be saved.
        :param num_receiver_per_file: int, the number of receivers in the receiver rad file per batch. Each
            batch is simulated the with separate calls of Radiance and generate results in different files.
        :param num_receiver_per_octree: int, the number of receivers per octree file.
        :param consider_octree: bool, if True, consider the octree file in the Radiance command.
        """
        # Check if the surface has viewed surfaces aka simulation is needed
        if len(radiative_surface_obj.viewed_surfaces_id_list) == 0:
            return [[]]
        # Get the rad_str of the emitter and receivers
        emitter_rad_str = radiative_surface_obj.rad_file_content
        receiver_rad_str_list: List[List[str]] = [self.get_radiative_surface(receiver_id).rad_file_content for
                                                  receiver_id in
                                                  radiative_surface_obj.viewed_surfaces_id_list]
        # Split the list of receiver rad str into batches
        receiver_rad_str_list_batches = split_into_batches(receiver_rad_str_list, num_receiver_per_file)
        # Generate the paths of the Radiance files
        name_emitter_rad_file, name_octree_file, name_receiver_rad_file, name_output_file = radiative_surface_obj.generate_rad_file_name()
        # Generate emitter file
        path_emitter_rad_file = self.generate_emitter_file(emitter_rad_str=emitter_rad_str,
                                                           path_emitter_folder=path_emitter_folder,
                                                           name_emitter_rad_file=name_emitter_rad_file)
        # Generate the octree file
        path_octree_file = self.generate_octree(receiver_rad_str_list=receiver_rad_str_list,
                                                path_octree_folder=path_octree_folder,
                                                name_octree_file=name_octree_file,
                                                num_receiver_per_octree=num_receiver_per_octree,
                                                consider_octree=consider_octree)
        # Generate the Radiance files for each batch
        argument_list_to_add = []
        for batch_index, batch_receiver_rad_str in enumerate(receiver_rad_str_list_batches):
            # Generate the receiver files
            path_receiver_rad_file = self.generate_receiver_files(
                receiver_rad_str_list=batch_receiver_rad_str,
                path_receiver_folder=path_receiver_folder,
                name_receiver_rad_file=name_receiver_rad_file,
                batch_index=batch_index)
            # Generate the output file
            path_output_file = self.get_path_output_file(path_output_folder=path_output_folder,
                                                         name_output_file=name_output_file,
                                                         batch_index=batch_index)
            # Add the Radiance argument to the list
            argument_list_to_add.append(
                [path_emitter_rad_file, path_receiver_rad_file, path_output_file, path_octree_file])

        return argument_list_to_add

    @staticmethod
    def generate_emitter_file(emitter_rad_str: str, path_emitter_folder: str,
                              name_emitter_rad_file: str) -> str:
        """
        Generate the emitter Radiance file.
        :param emitter_rad_str: str, the Radiance string of the emitter.
        :param path_emitter_folder: str, the folder path where the emitter Radiance files will be saved.
        :param name_emitter_rad_file: str, the name of the emitter Radiance file.
        :return path_emitter_rad_file: str, the path of the emitter Radiance file.
        """
        path_emitter_rad_file = os.path.join(path_emitter_folder, name_emitter_rad_file + ".rad")
        from_emitter_rad_str_to_rad_file(emitter_rad_str=emitter_rad_str,
                                         path_emitter_rad_file=path_emitter_rad_file)
        return path_emitter_rad_file

    @staticmethod
    def generate_receiver_files(receiver_rad_str_list: List[str], path_receiver_folder: str,
                                name_receiver_rad_file: str, batch_index: int):
        """
        Generate the receiver Radiance files.
        :param receiver_rad_str_list: [str], the list of receiver PolyData string for Radiance files.
        :param path_receiver_folder: str, the folder path where the receiver Radiance files will be saved.
        :param name_receiver_rad_file: str, the name of the receiver Radiance file.
        :param batch_index: int, the index of the batch.
        :return path_receiver_rad_file: str, the path of the receiver Radiance file.
        """
        path_receiver_rad_file = os.path.join(path_receiver_folder,
                                              name_receiver_rad_file + f"{batch_index}.rad")
        # Generate the files
        from_receiver_rad_str_to_rad_files(receiver_rad_str_list=receiver_rad_str_list,
                                           path_receiver_rad_file=path_receiver_rad_file)
        return path_receiver_rad_file

    @staticmethod
    def get_path_output_file(path_output_folder: str, name_output_file, batch_index: int) -> str:
        """
        Get the path of the output file.
        :param path_output_folder: str, the folder path where the output Radiance files will be saved.
        :param name_output_file: str, the name of the output Radiance file.
        :param batch_index: int, the index of the batch.
        :return path_output_file: str, the path of the output Radiance file.
        """
        path_output_file = os.path.join(path_output_folder, name_output_file + f"{batch_index}.txt")
        return path_output_file

    @staticmethod
    def generate_octree(receiver_rad_str_list: List[str], path_octree_folder: str, name_octree_file: str,
                        num_receiver_per_octree: int, consider_octree: bool = True) -> str:
        """
        Generate the octree file from the receiver PolyData.
        :param receiver_rad_str_list: [str], the list of receiver PolyData string for Radiance files.
        :param path_octree_folder: str, the folder path where the octree files will be saved.
        :param name_octree_file: str, the name of the octree file.
        :param num_receiver_per_octree: int, the number of receiver per rad file to convert to octree because
            of Radiance limitations.
        :param consider_octree: bool, if True, consider the octree file in the Radiance command.
        """
        if consider_octree:
            # Generate the octree file
            path_octree_file = from_receiver_rad_str_to_octree_file(
                receiver_rad_str_list=receiver_rad_str_list,
                path_folder_octree=path_octree_folder,
                name_octree_file=name_octree_file,
                num_receiver_per_octree=num_receiver_per_octree)
        else:
            path_octree_file = None

        return path_octree_file

    @staticmethod
    def create_vf_simulation_folders(path_root_simulation_folder: str, overwrite: bool = False,
                                     return_file_path_only: bool = False) -> (
            str, str, str, str, str):
        """
        Create the folders for the view factor simulation.
        :param path_root_simulation_folder: path of the root folder where the folders that will contain the Radiance
        input and output files will be created.
        :param overwrite: bool, if True, overwrite the root folders if they already exist.
        :param return_file_path_only: bool, if True, return only the path of the folders.
        :return: (str,str,str,str), the path of the emitter, octree, receiver and output folders.
        """

        path_emitter_folder = os.path.join(path_root_simulation_folder, "emitter")
        path_octree_folder = os.path.join(path_root_simulation_folder, "octree")
        path_receiver_folder = os.path.join(path_root_simulation_folder, "receiver")
        path_output_folder = os.path.join(path_root_simulation_folder, "output")
        if not return_file_path_only:
            create_folder(path_root_simulation_folder, overwrite=overwrite)
            create_folder(path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder,
                          overwrite=True)

        return path_emitter_folder, path_octree_folder, path_receiver_folder, path_output_folder

    #########################
    # View factor computation
    #########################

    def run_vf_computation(self, nb_rays: int = 10000):
        """
        Compute the view factor between multiple emitter and receiver with Radiance in batches.
        :param nb_rays: int, the number of rays to use.
        """
        self._sim_parameter_dict["num_rays"] = nb_rays
        for input_arg in self._radiance_argument_list:
            compute_vf_between_emitter_and_receivers_radiance(*input_arg, nb_rays=nb_rays)

    def run_vf_computation_in_parallel(self, nb_rays: int = 10000, num_workers=1, worker_batch_size=1,
                                       executor_type=ThreadPoolExecutor):
        """
        Compute the view factor between multiple emitter and receiver with Radiance in batches.
        :param nb_rays: int, the number of rays to use.
        :param num_workers: int, the number of workers to use for the parallelization.
        :param worker_batch_size: int, the size of the batch of commands to run in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        """
        self._sim_parameter_dict["num_rays"] = nb_rays
        parallel_computation_in_batches_with_return(
            func=compute_vf_between_emitter_and_receivers_radiance,
            input_tables=self._radiance_argument_list,
            executor_type=executor_type,
            worker_batch_size=worker_batch_size,
            num_workers=num_workers,
            nb_rays=nb_rays)

    def run_vf_computation_in_parallel_with_grouped_commands(self, nb_rays: int = 10000,
                                                             command_batch_size: int = 1, num_workers=1,
                                                             worker_batch_size=1,
                                                             executor_type=ThreadPoolExecutor):
        """
        Compute the view factor between multiple emitter and receiver with Radiance in batches.
        :param nb_rays: int, the number of rays to use.
        :param command_batch_size: int, the size of the batch of commands to run one after another
            in one command in each thread/process.
        :param num_workers: int, the number of workers to use for the parallelization.
        :param worker_batch_size: int, the size of the batch of commands to run in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        """

        self._sim_parameter_dict["num_rays"] = nb_rays
        # todo: add the octree to the arguments (and maybe generate it)
        input_batches = split_into_batches(self._radiance_argument_list, batch_size=command_batch_size)

        parallel_computation_in_batches_with_return(
            func=run_radiant_vf_computation_in_batches,
            input_tables=input_batches,
            executor_type=executor_type,
            worker_batch_size=worker_batch_size,
            num_workers=num_workers,
            nb_rays=nb_rays)

    ###############################
    # Read the results
    ###############################
    def read_vf_from_radiance_output_files(self, path_output_folder: str,
                                           num_workers=1, worker_batch_size=1):
        """
        Read the view factor from the Radiance output files.
        :param path_output_folder: str, the folder path where the Radiance output files are saved.
        :param num_workers: int, the number of workers to use for the parallelization.
        :param worker_batch_size: int, the size of the batch of commands to run in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        """
        _, _, _, path_output_folder = self.create_vf_simulation_folders(
            path_output_folder, return_file_path_only=True)
        parallel_computation_in_batches_with_return(
            func=object_method_wrapper,
            input_tables=[[radiative_surface_obj] for radiative_surface_obj in
                          self._radiative_surface_dict.values()],
            executor_type=ThreadPoolExecutor,
            worker_batch_size=worker_batch_size,
            num_workers=num_workers,
            method_name="read_vf_from_radiance_output_files",
            path_output_folder=path_output_folder)

    def adjust_radiative_surface_view_factors(self):
        """
        Adjust the pairs view factors of the RadiativeSurface objects.
        """
        # Technically, only half of the view factors need to be verified (one triangle of the matrix), but it will make
        # the code more complex, and not necessarily faster due to additional conditions to check.

        for surface_id_1, radiative_surface_obj_1 in self._radiative_surface_dict.items():
            vf_list = radiative_surface_obj_1.viewed_surfaces_view_factor_list()
            viewed_surfaces_id_list = radiative_surface_obj_1.get_viewed_surfaces_id_list()
            for surface_id_2, vf_1_2 in zip(viewed_surfaces_id_list, vf_list):
                radiative_surface_obj_2 = self.get_radiative_surface(surface_id_2)
                vf_2_1 = radiative_surface_obj_2.get_view_factor_from_surface_id(surface_id=surface_id_1)
                if self.is_view_factor_to_adjust(vf_1_2=vf_1_2, vf_2_1=vf_2_1,
                                                 num_rays=self._sim_parameter_dict["num_rays"]):
                    new_vf_1_2 = self.adjust_view_factors(vf_2_1=vf_2_1, area_1=radiative_surface_obj_1.area,
                                                          area_2=radiative_surface_obj_2.area)
                    radiative_surface_obj_1.set_view_factor_from_surface_id(surface_id=surface_id_2,
                                                                            view_factor=new_vf_1_2)

    @staticmethod
    def is_view_factor_to_adjust(vf_1_2: float, vf_2_1: float, num_rays: int) -> bool:
        """
        Adjust the view factors between two surfaces.
        :param vf_1_2: float, the view factor from surface 1 to surface 2.
        :param vf_2_1: float, the view factor from surface 2 to surface 1.
        :param num_rays: int, the number of rays used for the view factor computation with Radiance.
        :return: bool, True if the view factors vf_1_2 should be adjusted using vf_2_1, False otherwise.
        """
        if (vf_1_2 > vf_2_1  # No to adjust if vf_1_2 is smaller than vf_2_1
                or vf_2_1 < 10 / num_rays  # if vf_2_1 is too small, it is not reliable
                or vf_1_2 > vf_2_1 / 5.):  # The bounds could be adjusted, like this it does not ensure vf reciprocity
            return False
        else:
            return True

    @staticmethod
    def adjust_view_factors(vf_2_1: float, area_1: float, area_2: float):
        """
        Adjust the view factors using the reciprocity relation between view factors.
        :param vf_2_1: float, the view factor from surface 2 to surface 1.
        :param area_1: float, the area of the surface 1.
        :param area_2: float, the area of the surface 2.
        :return: float, the adjusted view factor from surface 1 to surface 2.
        """
        return vf_2_1 * area_2 / area_1

    # ----------------------------------------------------------
    # Check methods
    # ----------------------------------------------------------

    def check_num_worker_valid(self, num_worker, worker_type: str) -> int:
        """
        Check if the number of workers for parallel computing is valid.
        :param num_worker: The number of workers requested by the user.
        :param worker_type: str, the type of worker, either 'cpu' or 'io', having different limits.
        :return: adjusted number of workers if needed
        """
        if worker_type == "cpu":
            max_worker = self.MAX_WORKER_CPU_BOUND
            defaul_worker = self.DEFAULT_WORKER_CPU_BOUND
        elif worker_type == "io":
            max_worker = self.MAX_WORKER_IO_BOUND
            defaul_worker = self.DEFAULT_WORKER_IO_BOUND
        else:
            raise ValueError("The worker type is invalid. It must be either 'cpu' or 'io'.")
        if num_worker == 0 or num_worker is None:
            num_worker = defaul_worker
        elif max_worker < num_worker:
            warnings.warn(f"The number of workers requested is too high and will decrease the performances."
                          f"It will be set to {max_worker} instead.")
            num_worker = max_worker
        elif num_worker < 0 or isinstance(num_worker, float):
            raise ValueError(f"The number is invalid. It must be an integer between 0 and {max_worker} "
                             f"(maximum processes that your computer can handle before degrading performances.")
        return num_worker

    @staticmethod
    def check_min_vf_criterion(min_vf_criterion: float) -> float:
        """
        Check if the minimum view factor criterion is valid.
        :param min_vf_criterion: float, the minimum view factor criterion.
        :return: float, the minimum view factor criterion.
        """
        if min_vf_criterion is None:
            pass
        elif not isinstance(min_vf_criterion, float):
            raise ValueError("The minimum view factor criterion must be a float or None")
        elif min_vf_criterion < 0 or min_vf_criterion > 1:
            raise ValueError("The minimum view factor criterion must be between 0 and 1.")

        return min_vf_criterion


def flatten_table_to_lists(table):
    flattened = []
    for item in table:
        if isinstance(item, list) and any(isinstance(sub_item, list) for sub_item in item):
            flattened.extend(flatten_table_to_lists(item))  # Recursively flatten sublist
        elif not item == [] or isinstance(item, list):  # Ignore empty lists
            flattened.append(item)  # Add non-list item or innermost non-empty list to the flattened list
    flattened = [item for item in flattened if not item == []]  # Remove empty lists
    return flattened
