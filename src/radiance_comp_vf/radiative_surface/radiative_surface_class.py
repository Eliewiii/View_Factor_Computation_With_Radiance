"""
Class of surfaces for radiative simulations
"""

import os
import numpy as np
import numpy.typing as npt

from copy import deepcopy

from pyvista import PolyData
from typing import List

from geoplus import compute_numpy_array_planar_surface_area_and_centroid, \
    contour_numpy_array_planar_surface_with_holes, \
    compute_numpy_array_planar_surface_corners, numpy_array_surface_to_polydata, \
    compute_numpy_array_planar_surface_normal, \
    compute_exterior_boundary_of_numpy_array_planar_surface_with_contoured_holes

from ..utils import from_vertex_list_to_rad_str, generate_random_rectangles, read_ruflumtx_output_file, \
    compute_polydata_area, from_polydata_to_vertex_list, are_planar_surfaces_facing_each_other, \
    is_ray_between_surfaces_intersect_with_context

# parallel_processing, todo: Adust the import
from ..utils import parallel_computation_in_batches_with_return
from concurrent.futures import ProcessPoolExecutor

FORBIDDEN_CHARACTERS_NAME_SURFACE_RADIANCE = [' ', '-', '.', ',', ';', ':']


class RadiativeSurface:
    """
    Class of surfaces for radiative simulations
    """

    def __init__(self, identifier: str):
        self._identifier: str = self.adjust_identifier_for_radiance(
            identifier)  # Identifier, adjusted by the setter
        self._origin_identifier: str = identifier
        # Geometry
        self._vertex_list: npt.NDArray[np.float64] = None
        self._area: float = None
        self._centroid: npt.NDArray[np.float64] = None
        self._normal: npt.NDArray[np.float64] = None
        self._corner_vertices: npt.NDArray[np.float64] = None
        #
        self._num_viewed_surfaces: int = 0
        self._viewed_surfaces_dict: dict = {}
        self._viewed_surfaces_id_list: List = []
        self._viewed_surfaces_view_factor_list: List = []
        # VF properties
        self._vf_total: float = 0.  # Total view factor of the surface
        self._vf_to_surfaces: float = 0.  # Total view factor of the other surfaces
        self._vf_ground: float = 0.
        self._vf_sky: float = 0.
        self._vf_air: float = 0.
        # Radiative properties
        self._emissivity: float = None
        self._reflectivity: float = None
        self._transmissivity: float = None
        # Preprocessed data for Radiance
        self._rad_file_content: str = None

    def __str__(self):
        return f"RadiativeSurface(identifier='{self._identifier}')"

    def __deepcopy__(self, memo={}):
        new_radiative_surface = RadiativeSurface(self._identifier)
        new_radiative_surface.origin_identifier = self._origin_identifier
        new_radiative_surface.vertex_list = deepcopy(self._vertex_list, memo)
        new_radiative_surface.viewed_surfaces_id_list = deepcopy(self._viewed_surfaces_id_list, memo)
        new_radiative_surface.viewed_surfaces_view_factor_list = deepcopy(
            self._viewed_surfaces_view_factor_list, memo)
        new_radiative_surface.emissivity = self._emissivity
        new_radiative_surface.reflectivity = self._reflectivity
        new_radiative_surface.transmissivity = self._transmissivity
        new_radiative_surface.rad_file_content = self._rad_file_content

        return new_radiative_surface

    @classmethod
    def from_hb_face_object(cls, hb_face_object):
        """
        Convert a Honeybee face object to a RadiativeSurface object.
        :param hb_face_object: Honeybee face object.
        """
        """
        Will not be implemented eventually as it will require to import the Honeybee package (and thus install it).
        An additional package is developed to convert Honeybee objects to vertex lists.
        """

    @classmethod
    def from_vertex_list(cls, identifier: str, vertex_list: List[List[float]],
                         hole_list: List[List[List[float]]] = []) -> 'RadiativeSurface':
        """
        Convert a PolyData with wholes to a RadiativeSurface object.
        :param identifier: str, the identifier of the object.
        :param vertex_list: List[List[float]], the list of vertices of the object or a numpy array.
        :param hole_list: List[List[List[float]]], the list of vertices of the holes in the geometry or a numpy array.
        """
        vertex_array = np.array(vertex_list)
        # Convert the geometry array with wholes to a vertex list
        contoured_verterx_list = contour_numpy_array_planar_surface_with_holes(
            surface_boundary=vertex_array, hole_list=hole_list)

        # Compute the area, centroid and corner vertices
        radiative_surface_obj = cls(identifier)
        radiative_surface_obj.set_geometry(vertex_array=contoured_verterx_list)

        return radiative_surface_obj

    @classmethod
    def from_vertex_list_with_radiative_properties(cls, identifier: str, vertex_list: List[List[float]],
                                                   hole_list: List[List[List[float]]] = [],
                                                   emissivity: float = 0., reflectivity: float = 0.,
                                                   transmissivity: float = 0.):
        """
        Convert a PolyData with wholes to a RadiativeSurface object.
        :param identifier: str, the identifier of the object.
        :param vertex_list: List[List[float]], the list of vertices of the object.
        :param hole_list: List[List[List[float]]], the list of vertices of the holes in the geometry.
        :param emissivity: float, the emissivity of the surface.
        :param reflectivity: float, the reflectivity of the surface.
        :param transmissivity: float, the transmissivity of the surface.
        """
        radiative_surface_obj = cls.from_vertex_list(identifier=identifier, vertex_list=vertex_list,
                                                     hole_list=hole_list)
        radiative_surface_obj.set_radiative_properties(emissivity=emissivity, reflectivity=reflectivity,
                                                       transmissivity=transmissivity)
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
        vertex_list = polydata.points.tolist()
        radiative_surface_obj = cls(identifier)
        vertex_array = np.array(vertex_list)
        radiative_surface_obj.set_geometry(vertex_array=vertex_array)

        return radiative_surface_obj

    # =========================================================
    # Properties
    # =========================================================
    @property
    def identifier(self):
        return self._identifier

    @staticmethod
    def adjust_identifier_for_radiance(identifier: str) -> str:
        """
        Adjust the identifier for Radiance.
        Replace all the forbidden characters by underscores.
        This function might require adjustments when new forbidden characters are found.
        :param identifier: str, the identifier to adjust.
        """

        adjusted_identifier = identifier
        for forbidden_character in FORBIDDEN_CHARACTERS_NAME_SURFACE_RADIANCE:
            adjusted_identifier = adjusted_identifier.replace(forbidden_character, '_')
        if adjusted_identifier.replace("_", "") == "":
            raise ValueError(f"The identifier '{identifier}' must contain at least one valid character.")

        return adjusted_identifier

    @property
    def origin_identifier(self):
        return self._origin_identifier

    @property
    def vertex_list(self):
        return deepcopy(self._vertex_list)

    @property
    def area(self):
        return self._area

    @property
    def centroid(self):
        return deepcopy(self._centroid)

    @property
    def corner_vertices(self):
        return deepcopy(self._corner_vertices)

    @property
    def num_viewed_surfaces(self):
        return self._num_viewed_surfaces

    @property
    def viewed_surfaces_id_list(self):
        return list(self._viewed_surfaces_id_list)

    @property
    def viewed_surfaces_view_factor_list(self):
        return list(self._viewed_surfaces_view_factor_list)

    @property
    def vf_total(self):
        return self._vf_total

    @property
    def vf_to_surfaces(self):
        return self._vf_to_surfaces

    @property
    def vf_ground(self):
        return self._vf_to_surfaces

    @property
    def vf_sky(self):
        return self.vf_to_surfaces

    @property
    def vf_air(self):
        return self._vf_air

    @property
    def emissivity(self):
        return self._emissivity

    @property
    def reflectivity(self):
        return self._reflectivity

    @property
    def transmissivity(self):
        return self._transmissivity

    @property
    def rad_file_content(self):
        return self._rad_file_content

    def to_pyvista_polydata(self) -> PolyData:
        """
        Convert the RadiativeSurface object to a PyVista PolyData object.
        """
        return numpy_array_surface_to_polydata(
            compute_exterior_boundary_of_numpy_array_planar_surface_with_contoured_holes(self._vertex_list))

    # =========================================================
    # Method to get "processed" properties of the surface
    # =========================================================
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

    def get_index_viewed_surface(self, viewed_surface_id: str):
        """
        Get the index of a viewed surface.
        :param viewed_surface_id: str, the identifier of the viewed surface.
        """
        try:
            return self._viewed_surfaces_dict[viewed_surface_id]
        except KeyError:
            raise KeyError(f"The surface {viewed_surface_id} is not in the viewed surfaces list.")

    # =========================================================
    # Methods to set the properties of the surface
    # =========================================================
    def set_geometry(self, vertex_array: List[List[float]]):
        """
        Set the geometry of the surface.
        :param vertex_array: List[List[float]], the list of vertices of the object.
        """
        self._vertex_list = vertex_array
        self._rad_file_content = from_vertex_list_to_rad_str(vertices=vertex_array,
                                                             identifier=self._identifier)
        self._area, self._centroid = compute_numpy_array_planar_surface_area_and_centroid(
            surface_boundary=vertex_array)
        self._normal = compute_numpy_array_planar_surface_normal(surface_boundary=vertex_array)
        self._corner_vertices = compute_numpy_array_planar_surface_corners(surface_boundary=vertex_array)

    def set_radiative_properties(self, emissivity: float = 0., reflectivity: float = 0.,
                                 transmissivity: float = 0.):
        """
        Set the radiative properties of the surface.
        :param emissivity: float, the emissivity of the surface.
        :param reflectivity: float, the reflectivity of the surface.
        :param transmissivity: float, the transmissivity of the surface.
        """
        # Validate set properties
        if isinstance(emissivity, float) and 0 <= emissivity <= 1:
            self._emissivity = emissivity
        else:
            raise ValueError(f"Emissivity for surface {self._identifier} must be a float between 0 and 1.")
        if isinstance(reflectivity, float) and 0 <= reflectivity <= 1:
            self._reflectivity = reflectivity
        else:
            raise ValueError(f"Emissivity for surface {self._identifier} must be a float between 0 and 1.")
        if isinstance(transmissivity, float) and 0 <= transmissivity <= 1:
            self._transmissivity = transmissivity
        else:
            raise ValueError(f"Emissivity for surface {self._identifier} must be a float between 0 and 1.")

        # Check value integrity.
        if sum([self._emissivity, self._reflectivity, self._transmissivity]) == 1.:
            return
        elif sum([self._emissivity, self._reflectivity, self._transmissivity]) > 1.:
            raise ValueError(
                f"The sum of the emissivity, reflectivity and transmissivity of surface {self._identifier} "
                f"is not equal to 1.")
        # Adjust the properties if needed
        else:
            if self._emissivity == 0:  # Priority to emissivity
                self._emissivity = 1. - self._reflectivity - self._transmissivity
            elif self._reflectivity == 0:
                self._reflectivity = 1. - self._emissivity - self._transmissivity
            elif self._transmissivity == 0:
                self._transmissivity = 1. - self._emissivity - self._reflectivity

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

    # =========================================================
    # Obstruction Methods
    # =========================================================

    def are_other_surfaces_visible(self, radiative_surface_list: List['RadiativeSurface'],
                                   context_pyvista_polydata_mesh: PolyData):
        """

        :param radiative_surface_list:
        :param context_pyvista_polydata_mesh:
        :param other_para_args:
        :return:
        """
        visible_surfaces_id_list = []
        for radiative_surface in radiative_surface_list:
            if self._is_seeing_other_surface(radiative_surface, context_pyvista_polydata_mesh):
                visible_surfaces_id_list.append(radiative_surface._identifier)
        return visible_surfaces_id_list

    # @staticmethod
    # def are_radiative_surfaces_facing_each_other(radiative_surface_1: 'RadiativeSurface',
    #                                              radiative_surface_2: 'RadiativeSurface',
    #                                              context_pyvista_polydata_mesh: PolyData) -> bool:
    #     """
    #     Check if two surfaces are facing each other and thus can exchange radiative energy.
    #     Does not consider obstruction between the two surfaces. Use the do_radiative_surfaces_see_each_other method for
    #        this purpose.
    #     Intended for
    #     :param radiative_surface_1: RadiativeSurface, the first surface.
    #     :param radiative_surface_2: RadiativeSurface, the second surface.
    #     :return bool: True if the two surfaces are facing each other, False otherwise.
    #     """
    #     return [radiative_surface_1._is_seeing_other_surface(radiative_surface_2,
    #                                                          context_pyvista_polydata_mesh),
    #             radiative_surface_1._identifier, radiative_surface_2._identifier]

    def _is_seeing_other_surface(self, radiative_surface_2: 'RadiativeSurface',
                                 context_pyvista_polydata_mesh: PolyData) -> bool:
        """
        Check if two surfaces are facing each other.
        :param surface_1: RadiativeSurface, the first surface.
        :param surface_2: RadiativeSurface, the second surface.
        """
        # Check visibility without obstruction
        if not self._is_facing_other_surface(radiative_surface_2):
            return False
        # Ray tracing to check if there is an obstruction
        return not is_ray_between_surfaces_intersect_with_context(
            [self._centroid] + [corner for corner in self._corner_vertices],
            [radiative_surface_2._centroid] + [corner for corner in
                                               radiative_surface_2._corner_vertices],
            context_polydata_mesh=context_pyvista_polydata_mesh)

    def _is_facing_other_surface(self, radiative_surface_2: 'RadiativeSurface') -> bool:
        """
        Check if two surfaces are facing each other.
        :param surface_1: RadiativeSurface, the first surface.
        :param surface_2: RadiativeSurface, the second surface.
        """

        # Check if the normal vectors are facing each other
        return are_planar_surfaces_facing_each_other(self._corner_vertices,
                                                     radiative_surface_2._corner_vertices,
                                                     normal_1=self._normal,
                                                     normal_2=radiative_surface_2._normal)

    # =========================================================
    # VF related methods
    # =========================================================

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

    # =========================================================
    # File Generation Methods
    # =========================================================

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
        return f"emitter_{self._identifier}"

    def name_octree_file(self) -> str:
        """
        Generate the name of the octree file from the identifier without the extension.
        """
        return f"{self._identifier}"

    def name_receiver_file(self) -> str:
        """
        Generate the name of the receiver Radiance file from the identifier without the extension and batch number.
        """
        return f"receiver_{self._identifier}_batch_"

    def name_output_file(self) -> str:
        """
        Generate the name of the output Radiance file from the identifier without the extension and batch number.
        """
        return f"output_{self._identifier}_batch_"

    ##############################
    # Read VF Output Files Methods
    ##############################

    def read_vf_from_radiance_output_files(self, path_output_folder: str):
        """
        Read the view factors from the Radiance output files and add them to the _viewed_surfaces_view_factor_list
        attribute.
        :param path_output_folder:
        """

        list_output_files = [f for f in os.listdir(path_output_folder) if
                             f.startswith(self.name_output_file())]
        list_output_files.sort(
            key=lambda x: int(x.split("_")[-1].split(".")[0]))  # Order the files by batch number
        for output_file in list_output_files:
            if output_file.startswith(self.name_output_file()):
                self._viewed_surfaces_view_factor_list.extend(
                    read_ruflumtx_output_file(os.path.join(path_output_folder, output_file)))
