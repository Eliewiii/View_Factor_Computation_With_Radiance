"""
Test functions for the RadiativeSurface class.
"""
import os
import pytest

from time import time

from src.radiance_comp_vf import RadiativeSurfaceManager

def test_visibility():
    """
    todo: adjust the test and add tests for extrem cases

    Note: These function shouldn't be used with the debugger, the multiprocessing will can raise memory errors,
        though it should work fine in normal execution.
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
    # radiative_surface_manager._check_surface_visibility_sequential(mvfc=0.00001)
    # print(f"Sequential took: {time() - start:.2f} seconds")

    start = time()
    radiative_surface_manager.check_surface_visibility(mvfc=0.00000001, num_workers=16, ray_traced_check=True,
                                                       ray_tracing_among_all_all_corners=True)


    print(f"Multithreading took: {time() - start:.2f} seconds")

# todo: add tests for the other functions, the different check options as well as extreme cases
