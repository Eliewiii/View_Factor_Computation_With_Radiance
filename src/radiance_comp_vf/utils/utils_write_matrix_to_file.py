"""
Utility function to write a matrix to a file with optimized format for sparse matrices.
"""

from scipy import sparse


def save_sparse_npz(path_file, **sparse_matrices):
    """
    Save multiple sparse matrices to a single .npz file.
    :param path_file: str, path to the output .npz file.
    """
    # Prepare a dictionary to store sparse data
    sparse_data = {}

    # Loop through kwargs to process each sparse matrix
    for name, matrix in sparse_matrices.items():
        if sparse.issparse(matrix):
            # Store in CSR format for efficient storage
            sparse_data[name] = matrix
        else:
            raise ValueError(f"Matrix '{name}' is not sparse! Please provide a sparse matrix.")

    # Save all matrices to a compressed .npz file
    sparse.save_npz(path_file, sparse_data)

    print(f"Saved sparse matrices to '{path_file}' successfully!")