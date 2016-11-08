cimport cython
import numpy as np
cimport numpy as np

cpdef np.ndarray[double] lassim_function(np.ndarray[double] y,
                                         double t,
                                         np.ndarray[double] solution,
                                         np.ndarray[double] k_map,
                                         np.ndarray k_map_mask, int size)

cpdef np.ndarray[double, ndim=2] odeint1e8_lassim(np.ndarray[double] y0,
                                                  np.ndarray[double] t,
                                                  tuple args)
