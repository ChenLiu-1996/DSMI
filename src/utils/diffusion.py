import numpy as np
from sklearn.metrics import pairwise_distances
import graphtools
import warnings

warnings.filterwarnings("ignore")

# def compute_diffusion_matrix(X: np.array, k: int = 10):
#     G = graphtools.Graph(X, anisotropy=1.0, knn=k)
#     return G.diff_op.toarray()

# import phate
# def compute_diffusion_matrix(X: np.array, k: int = 10):
#     phate_op = phate.PHATE(random_state=0, n_jobs=1, knn_max=k, verbose=False)
#     _ = phate_op.fit_transform(X)
#     return phate_op.diff_op


def compute_diffusion_matrix(X: np.array,
                             k: int = 10,
                             density_norm_pow: float = 1.0):
    """
    Adapted from
    https://github.com/professorwug/diffusion_curvature/blob/master/diffusion_curvature/core.py

    Given input X returns a diffusion matrix P, as an numpy ndarray.
    Using "adaptive anisotropic" kernel
    Inputs:
        X: a numpy array of size n x d
        density_norm_pow: a float in [0, 1]
            == 0: classic Gaussian kernel
            == 1: completely removes density and provides a geometric equivalent to
                  uniform sampling of the underlying manifold
    Returns:
        P: a numpy array of size n x n that is the diffusion matrix
    """
    # Construct the distance matrix.
    D = pairwise_distances(X)

    sigma = median_heuristic(D)
    W = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp((-D**2) / (2 * sigma**2))

    # Anisotropic density normalization.
    if density_norm_pow > 0:
        Deg = np.diag(1 / np.sum(W, axis=1)**density_norm_pow)
        W = Deg @ W @ Deg

    # Turn affinity matrix into diffusion matrix.
    Deg = np.diag(1 / np.sum(W, axis=1)**0.5)
    P = Deg @ W @ Deg

    return P


def median_heuristic(
        D: np.ndarray,  # the distance matrix
):
    # estimate kernel bandwidth from distance matrix using the median heuristic
    # Get upper triangle from distance matrix (ignoring duplicates)
    h = D[np.triu_indices_from(D)]
    h = h**2
    h = np.median(h)
    nu = np.sqrt(h / 2)
    return nu
