# AUTOGENERATED! DO NOT EDIT! File to edit: ../02a_laziness_decay.ipynb.

# %% auto 0
__all__ = ['laziness_decay']

# %% ../02a_laziness_decay.ipynb 5
import numpy as np
from tqdm.notebook import trange
from .laziness import *
from .local_laziness import *
def laziness_decay(A, max_steps = 32, aperture = 20, neighborhood=10, smoothing=1, adaptive_neighborhood = False, non_lazy_diffusion=False,use_local_laziness=False):
    """Generates a matrix of the decaying laziness value per point over a range of t values

    Parameters
    ----------
    P : ndarray
        Diffusion matrix
    max_steps : int, optional
        Number of diffusion steps to take (starting from 1), by default 32
    aperture : int, optional
        The size of the initial diffusion neighborhood, by default 20
    smoothing : int, optional
        Number of smmoothing interations, by default 1

    Returns
    -------
    ndarray
        Each column is a set of laziness values per point at a specific time.
    """    
    if A.sum(axis=1)[0]==1:
        print("You seem to have passed the diffusion matrix. Skipping row normalization.")
        P = A
    else:
        D = np.diag(1/np.sum(A,axis=1))
        P = D @ A
    decay_per_point = np.empty((len(P),max_steps))
    if non_lazy_diffusion:
        print("Removing self-diffusion")
        P_zero_diagonal = (np.ones_like(P) - np.diag(np.ones(len(P))))*P
        D = np.diag(1/np.sum(P_zero_diagonal,axis=0))
        P = D @ P_zero_diagonal
    P_t = P
    for t in trange(1,max_steps+1):
        if use_local_laziness:
            laziness = local_laziness(A,diffusion_powers = t,aperture=aperture,neighborhood=neighborhood,smoothing=1)
        else:
            P_t = P_t @ P
            laziness = curvature(P,diffusion_powers=t,aperture=aperture,precomputed_powered_P=P_t,smoothing=smoothing,dynamically_adjusting_neighborhood=adaptive_neighborhood, non_lazy_diffusion=non_lazy_diffusion)
        decay_per_point[:,t-1] = laziness
    return decay_per_point
