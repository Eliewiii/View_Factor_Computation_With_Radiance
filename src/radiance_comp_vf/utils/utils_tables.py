"""
Utility functions for tables.
"""

from collections import defaultdict


def flatten_table_to_lists(table):
    flattened = []
    for item in table:
        if isinstance(item, list) and any(isinstance(sub_item, list) for sub_item in item):
            flattened.extend(flatten_table_to_lists(item))  # Recursively flatten sublist
        elif not item == [] or isinstance(item, list):  # Ignore empty lists
            flattened.append(item)  # Add non-list item or innermost non-empty list to the flattened list
    flattened = [item for item in flattened if not item == []]  # Remove empty lists
    return flattened


def sort_table_by_column(table, list_of_column_index_to_sort):
    """
    Sort a list of lists based on specified columns.

    :param table: List of lists to be sorted.
    :param list_of_column_index_to_sort: List of column indices to sort by, in priority order.
    :return: Sorted list of lists.
    """
    # Create a key for sorting based on the provided column indices
    return sorted(table, key=lambda x: tuple(x[i] for i in list_of_column_index_to_sort))


def merge_sublists_to_dict(data, index_key_column, index_merge_column):
    """
    Merges elements from a specified column of sublists that have the same key from another specified column.

    :param data: List of lists to merge.
    :param index_key_column: Index of the column to use as the dictionary key.
    :param index_merge_column: Index of the column to merge (extend lists for).
    :return: A dictionary where keys are the values from key_column, and values are merged lists from merge_column.
    :raises ValueError: If the data format is invalid or if columns are out of range.
    """
    # Check that the data is a list of lists
    if not isinstance(data, list) or not all(isinstance(sublist, list) for sublist in data):
        raise ValueError("Data must be a list of lists.")
    # Check that key_column and merge_column are valid indices for every sublist
    for sublist in data:
        if len(sublist) <= index_key_column or len(sublist) <= index_merge_column:
            raise ValueError(f"Each sublist must have at least {max(index_key_column, index_merge_column) + 1} columns.")
    # Check that the merge_column contains lists, if expecting to merge lists
    for sublist in data:
        if not isinstance(sublist[index_merge_column], list):
            raise ValueError(f"The merge_column (index {index_merge_column}) must contain lists to merge.")
    # Initialize a defaultdict to store merged results based on the key_column
    merged_data = defaultdict(list)

    for sublist in data:
        key = sublist[index_key_column]
        merged_data[key].extend(sublist[index_merge_column])  # Merge the elements of the specified merge_column

    return dict(merged_data)
