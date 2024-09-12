"""

"""

from src.radiance_comp_vf.utils.utils_visibility import are_planar_surfaces_facing_each_other



def test_are_planar_surfaces_seeing_each_other():
    vertices_1 = [[1, 2, 3], [4, 5, 6]]
    vertices_2 = [[7, 8, 9], [10, 11, 12]]
    normal_1 = [1, 0, 0]
    normal_2 = [-1, 0, 0]

    result = are_planar_surfaces_facing_each_other(vertices_1, vertices_2, normal_1=normal_1, normal_2=normal_2)
    print(result)