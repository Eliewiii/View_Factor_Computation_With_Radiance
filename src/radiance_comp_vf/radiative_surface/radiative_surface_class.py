"""
Class of surfaces for radiative simulations
"""

import os

import os

from copy import deepcopy
from numpy import ndarray
from pyvista import PolyData
from typing import List

from ..utils import from_polydata_to_dot_rad_str, generate_random_rectangles, read_ruflumtx_output_file, \
    compute_polydata_area,from_polydata_to_vertex_list


class RadiativeSurface:
    """
    Class of surfaces for radiative simulations
    """

    def __init__(self, identifier: str):
        self.identifier: str = identifier
        self.hb_identifier: str = None
        # Geometry
        self.vertex_list: ndarray = None
        self.area: float = None
        self.centroid: ndarray = None
        self.corner_vertices: List[ndarray] = None
        #
        self._num_viewed_surfaces: int = 0
        self._viewed_surfaces_dict: dict = {}
        self._viewed_surfaces_id_list: List = []
        self._viewed_surfaces_view_factor_list: List = []
        # VF properties
        self.vf_surface: float = 0.
        self.vf_ground: float = 0.
        self.vf_sky: float = 0.
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
        new_radiative_surface.vertex_list = deepcopy(self.vertex_list, memo)
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
    def from_surface_with_wholes(cls, identifier: str,geometry_array, whole_geometry_array_list, hb_identifier: str=None):
        """
        Convert a PolyData with wholes to a RadiativeSurface object.
        :param identifier: str, the identifier of the object.
        :param polydata: PolyData, the polydata to convert.
        """
        # Convert the geometry array with wholes to a vertex list

        # Compute the area, centroid and corner vertices


        radiative_surface_obj = cls(identifier)

        return radiative_surface_obj

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
        vertex_list = from_polydata_to_vertex_list(polydata)
        radiative_surface_obj.vertex_list = vertex_list
        radiative_surface_obj.rad_file_content = from_polydata_to_dot_rad_str(polydata, identifier)
        radiative_surface_obj.area = compute_polydata_area(polydata_obj=polydata)

        return radiative_surface_obj

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
        if not isinstance(viewed_surface_id_list, list):
            raise ValueError("The viewed surface identifier must be a list of strings.")
        for viewed_surface_id in viewed_surface_id_list:
            if not isinstance(viewed_surface_id, str):
                raise ValueError("The viewed surface identifier must be a string.")
            if viewed_surface_id not in self._viewed_surfaces_id_list:
                self._viewed_surfaces_id_list.append(viewed_surface_id)
                self._viewed_surfaces_dict[viewed_surface_id] = self._num_viewed_surfaces
                self._num_viewed_surfaces += 1
            else:
                raise ValueError(f"The surface {viewed_surface_id} is already in the viewed surfaces list.")

    def get_viewed_surfaces_id_list(self):
        """
        Get the list of identifiers of the surfaces viewed by the current surface.
        """
        return list(self._viewed_surfaces_id_list)

    def get_viewed_surfaces_view_factor_list(self):
        """
        Get the list of view factors of the surfaces viewed by the current surface.
        """
        return list(self._viewed_surfaces_view_factor_list)

    def get_view_factor_from_surface_id(self, surface_id: str):
        """
        Get the view factor of a surface viewed by the current surface.
        :param surface_id: str, the identifier of the viewed surface.
        """
        try:
            index = self.get_index_viewed_surface(surface_id)
            return self._viewed_surfaces_view_factor_list[index]
        except KeyError:
            raise KeyError(f"The surface {surface_id} is not in the viewed surfaces list.")

    def get_viewed_surfaces_dict(self):
        """
        Get the dictionary of viewed surfaces.
        """
        return dict(self._viewed_surfaces_dict)

    def get_index_viewed_surface(self, viewed_surface_id: str):
        """
        Get the index of a viewed surface.
        :param viewed_surface_id: str, the identifier of the viewed surface.
        """
        try:
            return self._viewed_surfaces_dict[viewed_surface_id]
        except KeyError:
            raise KeyError(f"The surface {viewed_surface_id} is not in the viewed surfaces list.")

    def adjust_view_factor(self, surface_id: str, view_factor: float):
        """"
        :param surface_id:
        :param view_factor:
        """
        try:
            index = self.get_index_viewed_surface(surface_id)
            self._viewed_surfaces_view_factor_list[index] = view_factor
        except KeyError:
            raise KeyError(f"The surface {surface_id} is not in the viewed surfaces list.")
        except IndexError:
            raise IndexError(
                f"The index of the surface is  {index}, but it looks like not VF was set for this surface yet.")

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
        return self.name_emitter_file(), self.name_octree_file(), self.name_receiver_file(), self.name_output_file()

    def name_emitter_file(self) -> str:
        """
        Generate the name of the emitter Radiance file from the identifier without the extension.
        """
        return f"emitter_{self.identifier}"

    def name_octree_file(self) -> str:
        """
        Generate the name of the octree file from the identifier without the extension.
        """
        return f"{self.identifier}"

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
    # Read VF Output Files Methods
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
