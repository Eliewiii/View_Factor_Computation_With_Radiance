"""

"""

import os
import numpy as np
from scipy.sparse import csr_matrix, save_npz, load_npz

from radiance_comp_vf.utils import save_sparse_to_npz_file, read_csr_matrices_from_npz

test_file_dir = os.path.dirname(os.path.abspath(__file__))

dir_generated_files = os.path.join(test_file_dir, "generated_file")

# Define a dense matrix
dense_matrix = np.array([
    [0, 0, 1, 0],
    [5, 0, 0, 0],
    [0, 0, 0, 3],
    [0, 2, 0, 0]
])

# Convert it to a CSR sparse matrix
sparse_matrix = csr_matrix(dense_matrix)


def test_save_sparse_to_npz_file():
    # Save to a compressed npz file
    # save_npz("sparse_matrix.npz", sparse_matrix, compressed=True)

    save_sparse_to_npz_file(dir_generated_files,**{"test_matrix":sparse_matrix})

    # Load the sparse matrix from file
    loaded_sparse_matrix=read_csr_matrices_from_npz(dir_generated_files, "test_matrix")
    print("Loaded Sparse Matrix:", loaded_sparse_matrix)

