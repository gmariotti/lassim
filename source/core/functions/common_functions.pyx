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
                                         np.ndarray[double] solution,
                                         np.ndarray[double] k_map,
                                         np.ndarray k_map_mask, int size):
    """
    Generates the list of functions to be "integrated"
    The form of the function is of the type
    dx/dt = -lambda * x + vmax / (1 + e-(SUMj kj * xj))
    :param y: value of each function during integration
    :param t: time sequence to be evaluated
    :param solution: decision vector received from an optimization. Represent a
    vector of type [lambda1,.., lambdan, vmax1,.., vmaxn, react1,.., reactm]
    :param k_map: a vector/map representing all the reactions between all the
    transcription factors
    :param k_map_mask: a mask of True/False of k_map used to identify which
    reactions are valid and which not
    :param size: number of transcription factors
    :return: The list of functions
    """
    cdef:
        np.ndarray[double] lambdas, vmax, k_values

    lambdas = solution[:size]
    vmax = solution[size: size * 2]
    k_values = solution[size * 2:]
    # map is a vector, but will be reshaped as a matrix size x size
    k_map[k_map_mask] = k_values

    # should return something like [val, val2, ..., valn]
    # k_values is a map with 0 where x is not present and the value of k when
    #  it is. Numpy will broadcast y to all the rows of k_values
    # sum_mat = np.dot(np.reshape(k_map, (size, size)), y.T)

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
    return -lambdas * y + vmax / (
        np.ones(y.size, dtype=Float) + np.exp(
            -np.dot(np.reshape(k_map, (size, size)), y.T)
        )
    )

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef np.ndarray[double, ndim=2] odeint1e8_lassim(np.ndarray[double] y0,
                                                  np.ndarray[double] t,
                                                  tuple args):
    return integrate.odeint(lassim_function, y0, t, args=args, mxstep=int(1e8))
