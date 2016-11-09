cimport cython
import numpy as np
cimport numpy as np

cpdef double perturbation_func_sequential(np.ndarray[double, ndim=2] pert_data,
                                          int num_tf, np.ndarray[double] y0,
                                          np.ndarray[double] sol_vector,
                                          np.ndarray[double] k_map,
                                          np.ndarray k_map_mask, int size, ode)
