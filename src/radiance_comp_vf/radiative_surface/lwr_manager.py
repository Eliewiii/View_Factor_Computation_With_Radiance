"""
Class that manages the whole LWR simulation, especially the RadiativeSurface objects.
"""

from .radiative_surface_manager_class import RadiativeSurfaceManager


class LWRManager(RadiativeSurfaceManager):
    """
    Class that manages the whole LWR simulation, especially the RadiativeSurface objects.
    """

    def __init__(self):
        super().__init__()
        #
        self.building_to_radiative_surface_dict = {}  # {building_id: [RadiativeSurface]}
        self.context_selection_parameters = None  # to adjust
        #
        self.matrix = None

    def set_context_selection_parameters(self, mvfc: float, nb_ray: int):
        """
        Set the parameters for the context selection.
        """
        # todo: implement this method for the integration with Urban_canopy
