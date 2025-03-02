"""
Utility function to write a matrix to a file with optimized format for sparse matrices.
"""

import numpy as np

from scipy import sparse


def save_sparse_to_npz_file(path_file, **sparse_matrices):
    """
    Save multiple sparse matrices to a single .npz file.
    :param path_file: str, path to the output .npz file.
    """
    # Prepare a dictionary to store sparse data
    sparse_data = {}

    # Loop through kwargs to process each sparse matrix
    for name, matrix in sparse_matrices.items():
        if sparse.issparse(matrix) :
            # Store in CSR format for efficient storage
            sparse_data[name] = matrix
        else:
            raise ValueError(f"Matrix '{name}' is not sparse! Please provide a sparse matrix.")

    # Save all matrices to a compressed .npz file
    np.savez_compressed(path_file, **sparse_data)

    print(f"Saved sparse matrices to '{path_file}' successfully!")

def read_csr_matrices_from_npz(path_file,*matrices_id):
    """
    Read multiple sparse matrices from a single .npz file.
    :param path_file:
    :param matrices_id:
    :return:
    """
    # Load the .npz file
    npz_data = np.load(path_file,allow_pickle=True)

    # Prepare a dictionary to store the loaded matrices
    matrix_dict = {}

    # Loop through the requested matrices
    for matrix_id in matrices_id:
        # Load the matrix in CSR format
        matrix_dict[matrix_id] = sparse.csr_matrix(npz_data[matrix_id])

    return matrix_dict