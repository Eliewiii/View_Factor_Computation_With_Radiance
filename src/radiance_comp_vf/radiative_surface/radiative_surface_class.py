"""
Class of surfaces for radiative simulations
"""

import os

from copy import deepcopy
from pyvista import PolyData
from typing import List

from ..utils import from_polydata_to_dot_rad_str, generate_random_rectangles, read_ruflumtx_output_file


class RadiativeSurface:
    """
    Class of surfaces for radiative simulations
    """

    def __init__(self, identifier: str):
        self.identifier: str = identifier
        self.hb_identifier: str = None
        self.polydata_geometry: PolyData = None
        self._viewed_surfaces_id_list: List = []
        self._viewed_surfaces_view_factor_list: List = []
        # Radiative properties
        self.emissivity: float = None
        self.reflectivity: float = None
        self.transmissivity: float = None
        # Preprocessed data for Radiance
        self.rad_file_content: str = None

    def __str__(self):
        return f"RadiativeSurface(identifier='{self.identifier}')"

    def __deepcopy__(self, memo={}):
        new_radiative_surface = RadiativeSurface(self.identifier)
        new_radiative_surface.hb_identifier = self.hb_identifier
        new_radiative_surface.polydata_geometry = deepcopy(self.polydata_geometry, memo)
        new_radiative_surface.viewed_surfaces_id_list = deepcopy(self.viewed_surfaces_id_list, memo)
        new_radiative_surface.viewed_surfaces_view_factor_list = deepcopy(
            self.viewed_surfaces_view_factor_list, memo)
        new_radiative_surface.emissivity = self.emissivity
        new_radiative_surface.reflectivity = self.reflectivity
        new_radiative_surface.transmissivity = self.transmissivity
        new_radiative_surface.rad_file_content = self.rad_file_content

        return new_radiative_surface

    @classmethod
    def from_hb_face_object(cls, hb_face_object):
        """
        Convert a Honeybee face object to a RadiativeSurface object.
        :param hb_face_object: Honeybee face object.
        """
        # Get the identifier

        # Create the RadiativeSurface object

        # Convert the Honeybee face object to a PolyData

        # Set the geometry and radiative properties

        # Make the Radiance string

    @classmethod
    def from_polydata(cls, identifier: str, polydata: PolyData):
        """
        Convert a PolyData to a RadiativeSurface object.
        :param identifier: str, the identifier of the object.
        :param polydata: PolyData, the polydata to convert.
        """
        if not isinstance(polydata, PolyData):
            raise ValueError(f"The polydata must be a PolyData object, not {type(polydata)}.")
        radiative_surface_obj = cls(identifier)
        radiative_surface_obj.polydata_geometry = polydata
        radiative_surface_obj.rad_file_content = from_polydata_to_dot_rad_str(polydata, identifier)

        return radiative_surface_obj

    @classmethod
    def from_random_rectangles(cls, id_index: int, num_random_rectangle: int = 10,
                               min_size: float = 0.001, max_size: float = 100,
                               max_distance_factor: float = 100,
                               parallel_coaxial_squares: bool = False):
        """
        Generate random rectangles and convert them to RadiativeSurface objects.
        :param id_index: int, the identifier index to name the surfaces.
        :param num_random_rectangle: int, the number of random rectangles.
        :param min_size: float, the minimum size of the rectangles.
        :param max_size: float, the maximum size of the rectangles.
        :param max_distance_factor: float, the maximum distance factor between the rectangles.
        :param parallel_coaxial_squares: bool, True to generate parallel coaxial squares.
        """
        if id_index % 50 == 0:
            print(id_index)
        ref_rectangle, random_rectangle_list = generate_random_rectangles(
            nb_random_rectangles=num_random_rectangle, min_size=min_size, max_size=max_size,
            max_distance_factor=max_distance_factor,
            parallel_coaxial_squares=parallel_coaxial_squares)
        # Set the id
        id_ref = f"ref_{id_index}"
        id_random_list = [f"random_{j}_ref_{id_index}" for j in range(num_random_rectangle)]
        # Convert the PolyData to RadiativeSurface objects
        ref_rad_surface_obj = RadiativeSurface.from_polydata(identifier=id_ref, polydata=ref_rectangle)
        random_rad_surface_obj_list = [
            RadiativeSurface.from_polydata(identifier=id_random, polydata=random_rectangle)
            for id_random, random_rectangle in zip(id_random_list, random_rectangle_list)]
        ref_rad_surface_obj.add_viewed_surfaces(id_random_list)

        return random_rad_surface_obj_list + [ref_rad_surface_obj]

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        if not isinstance(value, str):
            raise ValueError("The identifier must be a string.")
        if ' ' in value:
            raise ValueError("Identifier cannot contain spaces.")
        self._identifier = value

    def add_viewed_surfaces(self, viewed_surface_id_list: List[str]):
        """
        Add a viewed surface to the current surface.
        :param viewed_surface_id_list: str or [str], the identifier of the viewed surface.
        """
        for viewed_surface_id in viewed_surface_id_list:
            if not isinstance(viewed_surface_id, str):
                raise ValueError("The viewed surface identifier must be a string.")
            if viewed_surface_id not in self._viewed_surfaces_id_list:
                self._viewed_surfaces_id_list.append(viewed_surface_id)
            else:
                raise ValueError(f"The surface {viewed_surface_id} is already in the viewed surfaces list.")

    def get_viewed_surfaces_id_list(self):
        """
        Get the list of identifiers of the surfaces viewed by the current surface.
        """
        return list(self._viewed_surfaces_id_list)

    ##############################
    # File Generation Methods
    ##############################

    def generate_rad_file_name(self) -> (str, str, str, str):
        """
        Generate the name of the Radiance file from the identifier without the extension and batch number.
        :return: str, the name of the emitter Radiance file.
        :return: str, the name of the octree file.
        :return: str, the name of the receiver Radiance file.
        :return: str, the name of the output Radiance file.
        """
        return self.name_emitter_file(), self.name_octree_file, self.name_receiver_file(), self.name_output_file()

    def name_emitter_file(self) -> str:
        """
        Generate the name of the emitter Radiance file from the identifier without the extension.
        """
        return f"emitter_{self.identifier}"

    def name_octree_file(self) -> str:
        """
        Generate the name of the octree file from the identifier without the extension.
        """
        return f"{self.identifier}.oct"

    def name_receiver_file(self) -> str:
        """
        Generate the name of the receiver Radiance file from the identifier without the extension and batch number.
        """
        return f"receiver_{self.identifier}_batch_"

    def name_output_file(self) -> str:
        """
        Generate the name of the output Radiance file from the identifier without the extension and batch number.
        """
        return f"output_{self.identifier}_batch_"

    ##############################
    # Read Output files methods
    ##############################

    def read_vf_from_radiance_output_files(self, path_output_folder: str):
        """
        Read the view factors from the Radiance output files and add them to the _viewed_surfaces_view_factor_list
        attribute.
        :param path_output_folder:
        """
        list_output_files = [f for f in os.listdir(path_output_folder) if f.startswith(self.name_output_file())]
        for output_file in list_output_files:
            if output_file.startswith(self.name_output_file()):
                self._viewed_surfaces_view_factor_list.extend(
                    read_ruflumtx_output_file(os.path.join(path_output_folder, output_file)))
