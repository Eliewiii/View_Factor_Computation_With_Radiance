"""
Utility function to write a matrix to a file with optimized format for sparse matrices.
"""
import os

import numpy as np

from scipy.sparse import csr_matrix, save_npz, load_npz, issparse


def save_sparse_to_npz_file(path_dir, **sparse_matrices):
    """
    Save multiple sparse matrices to a single .npz file.
    :param path_file: str, path to the output .npz file.
    """
    # Check if directory exist
    if not os.path.isdir(path_dir):
        raise FileNotFoundError(f"The directory {path_dir} to write the matrices does not exist")
    # Loop through kwargs to process each sparse matrix
    for name, matrix in sparse_matrices.items():
        if not issparse(matrix):
            raise ValueError(f"Matrix '{name}' is not sparse! Please provide a sparse matrix.")

    for name, matrix in sparse_matrices.items():
        save_npz(os.path.join(path_dir, name), matrix, compressed=True)



def read_csr_matrices_from_npz(path_dir, *matrix_file_names):
    """
    Read multiple sparse matrices from a single .npz file.
    :param path_file:
    :param matrices_id:
    :return:
    """
    # Check if the files exist
    for name in matrix_file_names:
        if not os.path.isfile(os.path.join(path_dir, name + ".npz")):
            raise FileNotFoundError(f"The matrix file {os.path.join(path_dir, name + '.npz')} does not exist")
    #Load the matrices
    matrix_dict = {}

    for name in matrix_file_names:
        matrix_dict[name] = load_npz(os.path.join(path_dir, name + ".npz"))

    return matrix_dict
