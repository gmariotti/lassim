cimport cython
import numpy as np
cimport numpy as np

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

cpdef np.ndarray[double] lassim_function(np.ndarray[double] y, double t,
                                         np.ndarray[double] lambdas,
                                         np.ndarray[double] vmax,
                                         np.ndarray[double, ndim=2] k_map,
                                         np.ndarray[double] ones,
                                         np.ndarray[double] result)

cpdef np.ndarray[double, ndim=2] odeint1e8_lassim(np.ndarray[double] y0,
                                                  np.ndarray[double] t,
                                                  np.ndarray[double] sol_vector,
                                                  np.ndarray[double] k_map,
                                                  np.ndarray k_map_mask,
                                                  int size,
                                                  np.ndarray[double] result)

cpdef np.ndarray[double] lassim_matrix_function(
        np.ndarray[double] y, double t, np.ndarray[double, ndim=2] lambdas,
        np.ndarray[double, ndim=2] vmax, np.ndarray[double, ndim=2] k_map,
        np.ndarray[double] ones, np.ndarray[double] result)

cpdef np.ndarray[double, ndim=2] odeint1e8_lassim_matrix(
        np.ndarray[double] y0, np.ndarray[double] t,
        np.ndarray[double] sol_vector, np.ndarray[double] k_map,
        np.ndarray k_map_mask, int size, np.ndarray[double] result)