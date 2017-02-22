# noinspection PyUnresolvedReferences
cimport cython
import numpy as np
cimport numpy as np

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

cpdef double perturbation_func_sequential(np.ndarray[double, ndim=2] pert_data,
                                          int size, np.ndarray[double] y0,
                                          np.ndarray[double] sol_vector,
                                          np.ndarray[double] vector_map,
                                          np.ndarray vector_map_mask, ode)

cpdef double perturbation_peripheral(np.ndarray[double] pert_data, int size,
                                     np.ndarray[double] y0,
                                     np.ndarray[double] sol_vector,
                                     np.ndarray[double, ndim=2] pert_core,
                                     np.ndarray[double] vector_map,
                                     np.ndarray vector_map_mask, ode)
