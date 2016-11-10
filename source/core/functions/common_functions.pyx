cimport cython
import numpy as np
from scipy import integrate

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef np.ndarray[double] lassim_function(np.ndarray[double] y, double t,
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
    transcription factors. Must be a (y.size, y.size) matrix.
    :param ones: Vector of ones, same size of lambdas and vmax, for performance
    purposes.
    :param result: Vector containing the result of this call. It must be of the
    same size of y0. Needed for performance purposes.
    :return: The value of the ode system at time t.
    """

    # don't worry about RuntimeWarning for np.exp overflow. Even if a value
    # become inf, because is at the denominator it will make the result equal
    # to 0

    # numexpr seems 3 times slower than normal numpy. Maybe because the data
    # are not so big?
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
    ODE function wrapping a call to scipy.integrate.odeint with mxstep=1e8.
    :param y0: Values of y(0).
    :param t: Time sequence to evaluate.
    :param sol_vector: Solution vector for this system simulation.
    :param k_map: Map of the reactions as a vector. Must have size*size elements
    :param k_map_mask: Mask of the map of the reactions for map reshaping. Must
    have the same number of elements of k_map.
    :param size: Number of elements to consider.
    :param result: Vector containing the result of each integration call.
    Needed for performance purposes, it must of the same size of y0.
    :return: The values after integration of this system. The return values are
    the same of scipy.integrate.odeint
    """
    cdef:
        np.ndarray[double] lambdas, vmax, k_values
        np.ndarray[double] ones = np.ones(size)

    lambdas = sol_vector[:size]
    vmax = sol_vector[size: 2 * size]
    k_values = sol_vector[2 * size:]

    # map is a vector, but will be reshaped as a matrix size x size
    k_map[k_map_mask] = k_values
    return integrate.odeint(
        lassim_function, y0, t,
        args=(lambdas, vmax, np.reshape(k_map, (size, size)), ones, result),
        mxstep=int(1e8)
    )
