cimport cython
from multiprocessing.pool import Pool
from typing import Tuple, Callable

cimport numpy as np
import numpy as np
from numpy import linalg

from utilities.type_aliases import Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
# @cython.linetrace(True)
cpdef double perturbation_func_sequential(np.ndarray[double, ndim=2] pert_data,
                                          int num_tf, np.ndarray[double] y0,
                                          tuple ode_args, ode):
    cdef:
        unsigned int i, t_size
        double cost
        str time_str
        dict control_dict = {}
        list results = []
        np.ndarray[double, ndim=2] perturbations, times, simul
        np.ndarray[double] pert_diag, sol_vector, time_i, ret_value

    # first num_tf elements of each row is the value of the perturbations,
    # while the remaining elements of each row are start time and end time
    perturbations = pert_data[:, :num_tf]
    pert_diag = np.diagonal(perturbations)
    times = pert_data[:, num_tf:]
    # at each iteration, the value i in the variations vector is modified
    # accordingly to the value in the diagonal.
    # example:
    # 0 -> [v1 1 ... 1]
    # 1 -> [v1 v2 ... 1]
    # ....
    # n-1 -> [v1 v2 v3 ... vn-1]
    # control_dict = {}
    # results = []
    sol_vector = ode_args[0]
    for i in range(num_tf):
        time_i = times[i]
        time_str = str(time_i)
        # the control_dict takes trace of control calculations already evaluated
        # for that time sequence. It should not impact performance considering
        # the fact that dictionary are really fast in python
        if time_str not in control_dict:
            control_dict[time_str] = ode(y0, time_i, ode_args)
        sol_vector[i] = sol_vector[i] * pert_diag[i]
        simul = ode(y0, time_i, ode_args)
        tsize = time_i.size
        ret_value = control_dict[time_str][tsize - 1] / simul[tsize - 1]
        results.append(ret_value.flatten())

    # each row contains the vale in results
    sim_fold = np.array(results)

    nsim_fold = sim_fold - 1
    nsim_fold[nsim_fold > 2] = 2
    # for linalg.lstsq, nsim_fold must be a nx1 matrix while perturbations a
    # 1xn matrix, or n numpy vector
    lstsq_min = linalg.lstsq(
        np.reshape(nsim_fold, (nsim_fold.size, 1)), perturbations.flatten()
    )
    # lstsq_min = stats.linregress(
    #     nsim_fold.flatten(), perturbations.flatten()
    # )

    # at value 0 of lstsq_min there's the least-squares solution
    return np.sum(np.power(nsim_fold * lstsq_min[0], 2))

# extremely slow, creating a pool of processes everytime is really time
# consuming
def perturbation_func_with_pool(pert_data: Vector, num_tf: int, y0: Vector,
                                ode_args: Tuple[Vector, Vector, Vector, int],
                                ode: Callable[[Vector, Vector, Vector], Vector]
                                ) -> float:
    # starts a pool of processes based on the number of transcription factors
    with Pool(int(num_tf / 3)) as pool:

        # first num_tf elements of each row is the value of the perturbations,
        # while the remaining elements of each row are start time and end time
        perturbations = pert_data[:, :num_tf]
        pert_diag = np.diagonal(perturbations)
        times = pert_data[:, num_tf:]

        ones = np.ones(num_tf)
        # TODO - can be done in numpy somehow?
        values = []
        for i in range(0, num_tf):
            ones[i] = pert_diag[i]
            values.append((ones.copy(), times[i], y0, ode_args, ode))
        # FIXME - can be made asynchronous with pool.astarmap
        results = pool.starmap(pool_function, values)
        # each row contains the vale in results
        sim_fold = np.array(results)

    nsim_fold = sim_fold - 1
    nsim_fold[nsim_fold > 2] = 2
    # for linalg.lstsq, nsim_fold must be a nx1 matrix while perturbations a
    # 1xn matrix, or n numpy vector
    lstsq_min = linalg.lstsq(
        np.reshape(nsim_fold, (nsim_fold.size, 1)), perturbations.flatten()
    )
    # at value 0 of lstsq_min there's the least-squares solution
    cost = np.sum(np.power(nsim_fold * lstsq_min[0], 2))

    return cost

# it can't be in the previous function because it can't be pickled between
# processes
def pool_function(variations: Vector, time_seq: Vector, y0: Vector,
                  ode_args: Tuple[Vector, Vector, Vector, int],
                  ode: Callable[[Vector, Vector, Vector], Vector]
                  ) -> Vector:
    # called in another process, all is variables are protected from
    # concurrency problems
    sim_control = ode(y0, time_seq, ode_args)
    solution_vector = ode_args[0]
    v_size = variations.size
    # lambdas are changed based on the values in variations
    # runs in another process, so solution_vector is protected from
    # race conditions
    # first v_size arguments are the lambdas values
    solution_vector[:v_size] = solution_vector[:v_size] * variations
    simulation = ode(y0, time_seq, ode_args)
    # time0 should not be considered
    tsize = time_seq.size
    ret_value = sim_control[tsize - 1:] / simulation[tsize - 1:]
    return ret_value.flatten()
