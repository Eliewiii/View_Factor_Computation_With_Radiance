"""
Class that manages the whole LWR simulation, especially the RadiativeSurface objects.
"""

import os
import pickle

from typing import List

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from .radiative_surface_class import RadiativeSurface

from ..utils import from_emitter_receiver_rad_str_to_rad_files, split_into_batches, create_folder, \
    parallel_computation_in_batches_with_return, run_radiant_vf_computation_in_batches, \
    compute_vf_between_emitter_and_receivers_radiance, generate_random_rectangles


class RadiativeSurfaceManager:
    """
    Class that manages the whole RadiativeSurface objects.
    """

    def __init__(self):
        self._radiative_surface_dict: dict = {}
        self.context_octree = None
        self._radiance_argument_list: List[List] = []

    def __str__(self):
        return (f"RadiativeSurfaceManager with {len(self._radiative_surface_dict)} RadiativeSurface objects."
                f"list of RadiativeSurface objects: {list(self._radiative_surface_dict.keys())}")

    @classmethod
    def from_random_rectangles(cls, num_ref_rectangles: int = 1, num_random_rectangle: int = 10,
                               min_size: float = 0.01, max_size: float = 10,
                               max_distance_factor: float = 10, \
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
                                                    max_distance_factor: float = 10, \
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

    @classmethod
    def from_random_rectangles_in_parallel(cls, num_ref_rectangles: int = 1, num_random_rectangle: int = 10,
                                           min_size: float = 0.001, max_size: float = 100,
                                           max_distance_factor: float = 100,
                                           parallel_coaxial_squares: bool = False, num_workers=1,
                                           worker_batch_size=1,
                                           executor_type=ProcessPoolExecutor) -> "RadiativeSurfaceManager":
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
        :param num_workers: int, the number of workers to use for the parallelization
        :param worker_batch_size: int, the size of the batch of surfaces to process in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        :return: RadiativeSurfaceManager, the RadiativeSurfaceManager object.
        """
        radiative_surface_manager = cls()
        list_id_index = [[i] for i in range(num_ref_rectangles)]
        radiative_surface_list_to_add = parallel_computation_in_batches_with_return(
            func=RadiativeSurface.from_random_rectangles,
            input_tables=list_id_index,
            executor_type=executor_type,
            worker_batch_size=worker_batch_size,
            num_workers=num_workers,
            num_random_rectangle=num_random_rectangle,
            min_size=min_size, max_size=max_size,
            max_distance_factor=max_distance_factor,
            parallel_coaxial_squares=parallel_coaxial_squares)
        for radiative_surface_list in radiative_surface_list_to_add:
            radiative_surface_manager.add_radiative_surfaces(radiative_surface_list,
                                                             check_id_uniqueness=True)
        return radiative_surface_manager

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

    def make_context_octree(self):
        """
        Make the context octree for the Radiance simulation.
        """
        # todo: implement this method

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
            for viewed_surface_id in radiative_surface_obj.get_viewed_surfaces_id_list():
                if viewed_surface_id not in self._radiative_surface_dict:
                    raise ValueError(
                        f"The viewed surface {viewed_surface_id} of the surface {radiative_surface_obj.identifier} "
                        f"is not in the radiative surface manager.")

    def generate_radiance_inputs_for_all_surfaces(self, path_emitter_folder: str, path_receiver_folder: str,
                                                  path_output_folder: str, num_receiver_per_file: int = 1):
        """
        Generate the Radiance input files for all the RadiativeSurface objects.
        :param path_emitter_folder: str, the folder path where the emitter Radiance files will be saved.
        :param path_receiver_folder: str, the folder path where the receiver Radiance files will be saved.
        :param path_output_folder: str, the folder path where the output Radiance files will be saved.
        :param num_receiver_per_file: int, the number of receivers in the receiver rad file per batch.
            From testing, it seems that the number of receivers per batch has a limit around 100, but it might be computer dependant.
        """
        self.check_all_viewed_surfaces_in_manager()
        # Generate the folder if they don't exist
        create_folder(path_emitter_folder, path_receiver_folder, path_output_folder, overwrite=True)
        #

        argument_list_to_add = []
        # Generate the Radiance files for each surface
        for radiative_surface_obj in self._radiative_surface_dict.values():
            argument_list_to_add.extend(
                self.generate_radiance_inputs_for_one_surface(radiative_surface_obj, path_emitter_folder,
                                                              path_receiver_folder, path_output_folder,
                                                              num_receiver_per_file))

        self._add_argument_to_radiance_argument_list(argument_list_to_add)

    def generate_radiance_inputs_for_all_surfaces_in_parallel(self, path_emitter_folder: str,
                                                              path_receiver_folder: str,
                                                              path_output_folder: str,
                                                              num_receiver_per_file: int = 1,
                                                              num_workers=1, worker_batch_size=1,
                                                              executor_type=ThreadPoolExecutor):
        """
        Generate the Radiance input files for all the RadiativeSurface objects in parallel.
        :param path_emitter_folder: str, the folder path where the emitter Radiance files will be saved.
        :param path_emitter_folder: str, the folder path where the emitter Radiance files will be saved.
        :param path_receiver_folder: str, the folder path where the receiver Radiance files will be saved.
        :param path_output_folder: str, the folder path where the output Radiance files will be saved.
        :param num_receiver_per_file: int, the number of receivers in the receiver rad file per batch.
        :param num_workers: int, the number of workers to use for the parallelization
        :param worker_batch_size: int, the size of the batch of surfaces to process in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        """
        # Generate the folder if they don't exist
        create_folder(path_emitter_folder, path_receiver_folder, path_output_folder, overwrite=True)
        # Split t
        argument_list_to_add = parallel_computation_in_batches_with_return(
            func=self.generate_radiance_inputs_for_one_surface,
            input_tables=[[radiative_surface_obj] for radiative_surface_obj in
                          self._radiative_surface_dict.values()],
            executor_type=executor_type,
            worker_batch_size=worker_batch_size,
            num_workers=num_workers,
            path_emitter_folder=path_emitter_folder,
            path_receiver_folder=path_receiver_folder,
            path_output_folder=path_output_folder,
            num_receiver_per_file=num_receiver_per_file)

        argument_list_to_add = flatten_table_to_lists(argument_list_to_add)

        self._add_argument_to_radiance_argument_list(argument_list_to_add)

    def generate_radiance_inputs_for_one_surface(self, radiative_surface_obj: RadiativeSurface,
                                                 path_emitter_folder: str, path_receiver_folder: str,
                                                 path_output_folder: str, num_receiver_per_file: int = 1):
        """
        Generate the Radiance input files for one RadiativeSurface object.
        :param radiative_surface_obj: RadiativeSurface, the RadiativeSurface object.
        :param path_emitter_folder: str, the folder path where the emitter Radiance files will be saved.
        :param path_receiver_folder: str, the folder path where the receiver Radiance files will be saved.
        :param path_output_folder: str, the folder path where the output Radiance files will be saved.
        :param num_receiver_per_file: int, the number of receivers in the receiver rad file per batch. Each batch is
            simulated the with separate calls of Radiance and generate results in different files.
        """
        # Check if the surface has viewed surfaces aka simulation is needed
        if len(radiative_surface_obj.get_viewed_surfaces_id_list()) == 0:
            return [[]]
        # Get the rad_str of the emitter and receivers
        emitter_rad_str = radiative_surface_obj.rad_file_content
        receiver_rad_str_list = [self.get_radiative_surface(receiver_id).rad_file_content for receiver_id in
                                 radiative_surface_obj.get_viewed_surfaces_id_list()]
        receiver_rad_str_list_batches = split_into_batches(receiver_rad_str_list, num_receiver_per_file)
        # Generate the paths of the Radiance files
        name_emitter_rad_file, name_receiver_rad_file, name_output_file = radiative_surface_obj.generate_rad_file_name()
        path_emitter_rad_file = os.path.join(path_emitter_folder, name_emitter_rad_file + ".rad")
        #
        argument_list_to_add = []
        # Generate the Radiance files for each batch
        for i, batch in enumerate(receiver_rad_str_list_batches):
            path_receiver_rad_file = os.path.join(path_receiver_folder, name_receiver_rad_file + f"{i}.rad")
            path_output_file = os.path.join(path_output_folder, name_output_file + f"{i}.txt")
            # Generate the files
            from_emitter_receiver_rad_str_to_rad_files(emitter_rad_str=emitter_rad_str,
                                                       receiver_rad_str_list=batch,
                                                       path_emitter_rad_file=path_emitter_rad_file,
                                                       path_receiver_rad_file=path_receiver_rad_file)

            # Add the Radiance argument to the list
            argument_list_to_add.append([path_emitter_rad_file, path_receiver_rad_file, path_output_file])

        return argument_list_to_add

    def run_vf_computation(self, nb_rays: int = 10000):
        """
        Compute the view factor between multiple emitter and receiver with Radiance in batches.
        :param nb_rays: int, the number of rays to use.
        :param command_batch_size: int, the size of the batch of commands to run one after another
            in one command in each thread/process.
        :param num_workers: int, the number of workers to use for the parallelization.
        :param worker_batch_size: int, the size of the batch of commands to run in parallel.
        :param executor_type: the type of executor to use for the parallelization.
        """
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
        # todo: add the octree to the arguments (and maybe generate it)

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
        # todo: add the octree to the arguments (and maybe generate it)
        input_batches = split_into_batches(self._radiance_argument_list, batch_size=command_batch_size)

        parallel_computation_in_batches_with_return(
            func=run_radiant_vf_computation_in_batches,
            input_tables=input_batches,
            executor_type=executor_type,
            worker_batch_size=worker_batch_size,
            num_workers=num_workers,
            nb_rays=nb_rays)


def flatten_table_to_lists(table):
    flattened = []
    for item in table:
        if isinstance(item, list) and any(isinstance(sub_item, list) for sub_item in item):
            flattened.extend(flatten_table_to_lists(item))  # Recursively flatten sublist
        elif not item == [] or isinstance(item, list):  # Ignore empty lists
            flattened.append(item)  # Add non-list item or innermost non-empty list to the flattened list
    flattened = [item for item in flattened if not item == []]  # Remove empty lists
    return flattened
