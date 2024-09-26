"""

"""

from src.radiance_comp_vf.utils.utils_tables import sort_table_by_column

def test_sort_table_by_column():
    data = [
        ['apple', 5, [1, 2, 3]],
        ['banana', 3, [4, 5, 6]],
        ['apple', 2, [7, 8, 9]],
        ['banana', 1, [10, 11, 12]]
    ]

    # Sort by the first element (index 0)
    sorted_data = sort_table_by_column(data, [0])
    assert sorted_data == [['apple', 5, [1, 2, 3]], ['apple', 2, [7, 8, 9]], ['banana', 3, [4, 5, 6]],
                           ['banana', 1, [10, 11, 12]]]
    # Sort by the second element (index 1)
    sorted_data = sort_table_by_column(data, [1])
    assert sorted_data == [['banana', 1, [10, 11, 12]], ['apple', 2, [7, 8, 9]], ['banana', 3, [4, 5, 6]],
                           ['apple', 5, [1, 2, 3]]]
    # Sort by the first element (index 0) and then by the second element (index 1)
    sorted_data = sort_table_by_column(data, [0, 1])
    assert sorted_data == [['apple', 2, [7, 8, 9]], ['apple', 5, [1, 2, 3]], ['banana', 1, [10, 11, 12]],
                           ['banana', 3, [4, 5, 6]]]
