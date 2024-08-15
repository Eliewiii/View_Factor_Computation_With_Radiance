"""
Utils functions to genrate batches of input data for parallel computing
"""

from typing import List


def split_into_batches(input_table: List[list], batch_size: int) -> List[List[list]]:
    """
    Splits multiple lists of data into batches of a specified size.

    :param input_table: List of lists, data to be split into batches.
    :param batch_size: Int, size of each batch.
    :return: List of batches.
    """
    num_items = len(input_table)
    if num_items < batch_size:
        return [input_table]
    batches = []
    for start in range(0, num_items, batch_size):
        end = min(start + batch_size, num_items)
        batch = input_table[start: end]
        batches.append(batch)
    return batches


if __name__ == "__main__":
    input_table = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [10, 11, 12]]
    batch_size = 2
    print(split_into_batches(input_table, batch_size))  # [[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]
