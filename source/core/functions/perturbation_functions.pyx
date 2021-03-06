cimport cython

cimport numpy as np
import numpy as np
from numpy import linalg
# from scipy import linalg

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef double perturbation_func_sequential(np.ndarray[double, ndim=2] pert_data,
                                          int size, np.ndarray[double] y0,
                                          np.ndarray[double] sol_vector,
                                          np.ndarray[double] vector_map,
                                          np.ndarray vector_map_mask, ode):
    """
    Sequential function for evaluation of the impact of the perturbations over
    the "normal" behaviour of the current system.
    :param pert_data: A num_tf * num_tf matrix representing the perturbations
    data.
    :param size: Number of elements to consider.
    :param y0: Starting values for integration.
    :param sol_vector: Current solution vector. Is responsibility of the ode
    to interpret it. The only supposition is that the perturbations diagonal
    influences the first num_tf values in the array.
    :param vector_map: Map for the ode.
    :param vector_map_mask: Mask of the map for the ode.
    :param ode: Function for performing the ode
    :return: Value of the impact of the perturbations over the "normal" system
    """
    cdef:
        int i
        unsigned int t_size, sim_size = size * size
        double cost
        str time_str
        dict control_dict = {}
        # first num_tf elements of each row is the value of the perturbations,
        # while the remaining elements of each row are start time and end time
        np.ndarray[double, ndim=2] perturbations = pert_data[:, :size]
        np.ndarray[double, ndim=2] times = pert_data[:, size:]
        np.ndarray[double, ndim=2] simulation = np.empty((sim_size, 1))
        np.ndarray[double, ndim=2] ones = np.ones((sim_size, 1))
        np.ndarray[double, ndim=2] temp_simul
        np.ndarray[double] pert_diag = np.diagonal(perturbations)
        np.ndarray[double] time_i, ret_value
        np.ndarray[double] res_container = np.empty(size)

    # number of columns of times
    t_size = times.shape[1]
    temp_simul = np.empty((t_size, size))
    # at each iteration, the value i in the variations vector is modified
    # accordingly to the value in the diagonal.
    # example:
    # 0 -> [v1 1 ... 1]
    # 1 -> [v1 v2 ... 1]
    # ....
    # n-1 -> [v1 v2 v3 ... vn-1]
    for i in range(size):
        time_i = times[i]
        # FIXME - find a better way
        time_str = str(time_i)

        # the control_dict takes trace of control calculations already evaluated
        # for that time sequence. It should not impact performance considering
        # the fact that dictionary are really fast in python
        if time_str not in control_dict:
            control_dict[time_str] = ode(
                y0, time_i, sol_vector, vector_map, vector_map_mask, size,
                res_container
            )
        sol_vector[i] = sol_vector[i] * pert_diag[i]
        temp_simul = ode(
            y0, time_i, sol_vector, vector_map, vector_map_mask, size,
            res_container
        )
        simulation[i * size: (i + 1) * size] = np.reshape(
            temp_simul[t_size - 1] / control_dict[time_str][t_size - 1],
            (size, 1)
        )

    # each row contains the vale in results
    simulation -= ones
    simulation[simulation > 2] = 2

    # for linalg.lstsq, sim_fold must be a nx1 matrix while perturbations a
    # 1xn matrix, or n numpy vector
    lstsq_min = linalg.lstsq(
        simulation, perturbations.flatten()
    )

    # at value 0 of lstsq_min there's the least-squares solution
    # return np.sum(np.power(
    #     sim_fold * lstsq_min[0] - perturbations.reshape((s_size, 1)), 2
    # ))
    # at value 1 there's the sums of residuals - squared Euclidean 2-norm
    return lstsq_min[1]
