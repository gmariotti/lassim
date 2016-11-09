cimport cython
import numpy as np
from scipy import integrate

from utilities.type_aliases import Float

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef np.ndarray[double] lassim_function(np.ndarray[double] y,
                                         double t,
                                         np.ndarray[double] lambdas,
                                         np.ndarray[double] vmax,
                                         np.ndarray[double, ndim=2] k_map,
                                         np.ndarray[double] ones,
                                         np.ndarray[double] result):
    """
    Generates the list of functions to be "integrated"
    The form of the function is of the type
    dx/dt = -lambda * x + vmax / (1 + e-(SUMj kj * xj))
    :param y: value of each function during integration.
    :param t: time value at this point in the integration. Not used.
    :param lambdas: Vector of lambdas in form [lambda_1, lambda_2,.., lambda_n]
    :param vmax: Vector of vmax in form [vmax_1, vmax_2,.., vmax_n]
    :param k_map: a matrix representing all the reactions between all the
    transcription factors.
    :param ones: Vector of ones, same size of lambdas and vmax, for performance
    purposes.
    :param result: Vector containing the result of the function. Done for
    performance purposes.
    :return: The value of the ode system at time t.
    """

    # don't worry about RuntimeWarning for np.exp overflow. Even if a value
    # become inf, because is at the denominator it will make the result equal
    # to 0

    # numexpr seems 3 times slower than normal numpy. Maybe because the data
    # are not so big?
    # ones = np.ones(y.size, dtype=Float)
    # return ne.evaluate("-lambdas * y + vmax / (ones + exp(-sum_mat))")
    # return -lambdas * y + vmax / (
    #     np.ones(y.size, dtype=Float) + np.exp(-sum_mat)
    # )

    # sum_mat = -np.dot(np.reshape(k_map, (size, size)), y.T)
    result = -lambdas * y + vmax / (ones + np.exp(-np.dot(k_map, y.T)))
    return result

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef np.ndarray[double, ndim=2] odeint1e8_lassim(np.ndarray[double] y0,
                                                  np.ndarray[double] t,
                                                  np.ndarray[double] sol_vector,
                                                  np.ndarray[double] k_map,
                                                  np.ndarray k_map_mask,
                                                  int size,
                                                  np.ndarray[double] result):
    """
    TODO
    :param y0:
    :param t:
    :param sol_vector:
    :param k_map:
    :param k_map_mask:
    :param size:
    :param result:
    :return:
    """
    cdef:
        np.ndarray[double] lambdas, vmax, k_values, ones

    lambdas = sol_vector[:size]
    vmax = sol_vector[size: 2 * size]
    k_values = sol_vector[2 * size:]

    # map is a vector, but will be reshaped as a matrix size x size
    k_map[k_map_mask] = k_values
    ones = np.ones(size, dtype=Float)
    return integrate.odeint(
        lassim_function, y0, t,
        args=(lambdas, vmax, np.reshape(k_map, (size, size)), ones, result),
        mxstep=int(1e8)
    )
