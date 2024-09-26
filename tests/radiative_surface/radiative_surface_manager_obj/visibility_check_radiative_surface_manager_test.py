"""
Test functions for the RadiativeSurface class.
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


def test_visibility():
    """
    todo: adjust the test
    """
    num_random_rectangle = 10
    num_ref_rectangles = 1
    radiative_surface_manager = RadiativeSurfaceManager.from_random_rectangles(
        num_ref_rectangles=num_ref_rectangles,
        num_random_rectangle=num_random_rectangle,
        min_size=1, max_size=1,
        max_distance_factor=10,
        parallel_coaxial_squares=False
    )

    # sequential
    start = time()
    # radiative_surface_manager.check_surface_visibility_sequential(mvfc=0.00001)
    # print(f"Sequential took: {time() - start:.2f} seconds")

    start = time()
    radiative_surface_manager.check_surface_visibility(mvfc=0.00000001, num_workers=16, ray_traced_check=True,
                                                       ray_tracing_among_all_all_corners=True)
    print(f"Multithreading took: {time() - start:.2f} seconds")
