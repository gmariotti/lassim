from typing import List, Tuple, Callable

import numpy as np

from core.lassim_problem import LassimProblem, LassimProblemFactory
from core.utilities.type_aliases import Vector, Float

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class NetworkProblem(LassimProblem):
    """
    This class is a representation of the optimization problem for solving a
    network problem, with a fixed, immutable core and mutable peripherals. It
    is completely independent on how the equations system is designed and
    solved.
    For compatibility purposes, the _s_ variables must be set before the
    creation of the problem. This is needed for extending a PyGMO.problem.base
    class and avoid exceptions during execution.
    [!] NOT THREAD SAFE
    """

    _s_dim = 0
    _s_bounds = ([], [])
    _s_cost_data = (np.empty(1), np.empty(1), np.empty(1))
    _s_core_data = (np.empty(1), np.empty(1))
    _s_map_tuple = (np.empty(1), np.empty(1))
    _s_y0 = np.empty(1)
    _s_ode_function = None

    def __init__(self, dim: int = 1, known_sol: List[Vector] = None):
        """
        Constructor of a NetworkProblem.

        :param dim: not used, present just for avoiding PyGMO crashes. Use
            instead _s_dim for the problem dimension.
        :param known_sol: List of known solutions previously found. They seems
            to not help for speeding the optimization process, used them as a
            comparison with the optimization results.
        """

        super(NetworkProblem, self).__init__(NetworkProblem._s_dim)

        # for numpy exp overflow
        np.seterr(over="ignore")

        # only arguments that should be public
        self.vector_map, self.vector_map_mask = NetworkProblem._s_map_tuple
        if self.vector_map.shape != self.vector_map_mask.shape:
            raise ValueError(
                "Map shape {} is different from mask shape {}".format(
                    self.vector_map.shape, self.vector_map_mask.shape
                ))

        # set parameters for the objective function
        self._net_data, self._sigma, self._time = NetworkProblem._s_cost_data
        self._y0 = NetworkProblem._s_y0

        try:
            np.broadcast(self._net_data, self._sigma)
        except ValueError:
            raise ValueError(
                "Data shape {} is incompatible with sigma shape {}".format(
                    self._net_data.shape, self._sigma.shape
                ))
        self._core_data, self._core_mask = NetworkProblem._s_core_data
        if self._core_data.shape != self._core_mask:
            raise ValueError(
                "Core data shape {} is incompatible with mask shape {}".format(
                    self._core_data.shape, self._core_mask.shape
                ))

        self._sigma2 = np.power(self._sigma, 2)
        self._size = NetworkProblem._s_y0.size

        # sets the lower bounds and upper bounds
        lower_bounds, upper_bounds = NetworkProblem._s_bounds
        self.set_bounds(lower_bounds, upper_bounds)

        if known_sol is not None:
            self.best_x = [vector.tolist() for vector in known_sol]

        # these variables are used for performance efficiency
        self._result_mem = np.empty(self._size)
        self._cost_mem = np.empty(self._net_data.shape)

    def _objfun_impl(self, x):
        """
        Calculates the objective function for this problem with x as decision
        vector.

        :param x: Tuple containing the value of each parameter to optimize.
        :return: A tuple of a single value, containing the cost for this value
            of x.
        """

        # the solution vector represent the variables for the core equations,
        # that are fixed at creation time, plus the variables for the peripheral
        # that varies between _objfun_impl calls.
        solution_vector = self._core_data.copy()
        solution_vector[self._core_mask] = np.fromiter(x, dtype=Float)

        results = NetworkProblem._s_ode_function(
            self._y0, self._time, solution_vector,
            self.vector_map, self.vector_map_mask, self._size, self._result_mem
        )
        norm_result = np.divide(
            results[:, self._res_pos], np.amax(results[:, self._res_pos])
        )
        cost = np.sum(np.divide(np.power(
            np.subtract(self._net_data, norm_result), 2, out=self._cost_mem),
            self._sigma2, out=self._cost_mem)
        )
        return (cost,)

    def __get_deepcopy__(self):
        return NetworkProblem(dim=self.dimension)

    def __deepcopy__(self, memodict={}):
        return self.__get_deepcopy__()

    def __copy__(self):
        return self.__get_deepcopy__()


class NetworkWithPerturbationsProblem(NetworkProblem):
    """
    This class is a representation of the optimization problem for solving a
    network problem, with a fixed, immutable core and mutable peripherals but
    with also perturbations data available.
    It is completely independent on how the equations system is designed and
    solved.
    For compatibility purposes, the _s_ variables must be set before the
    creation of the problem. This is needed for extending a PyGMO.problem.base
    class and avoid exceptions during execution.
    [!] NOT THREAD SAFE
    """

    _s_pert_function = None
    _s_pert_core = np.empty(1)
    _s_pert_data = np.empty(1)
    _s_pert_factor = 0

    def __init__(self, dim: int = 1, known_sol: List[Vector] = None):
        """
        Constructor of NetworkWithPerturbationsProblem.

        :param dim: not used, present just for avoiding PyGMO crashes. Use
            instead _s_dim for the problem dimension.
        :param known_sol: List of known solutions previously found. They seems
            to not help for speeding the optimization process, used them as a
            comparison with the optimization results.
        """

        self._pcore = NetworkWithPerturbationsProblem._s_pert_core
        self._pdata = NetworkWithPerturbationsProblem._s_pert_data
        self._factor = NetworkWithPerturbationsProblem._s_pert_factor
        super(NetworkWithPerturbationsProblem, self).__init__(
            NetworkProblem._s_dim, known_sol
        )

    def _objfun_impl(self, x):
        """
        Calculates the objective function for this problem with x as decision
        vector.

        :param x: Tuple containing the value of each parameter to optimize.
        :return: A tuple of a single value, containing the cost for this value
            of x.
        """

        cost = super(NetworkWithPerturbationsProblem, self)._objfun_impl(x)[0]
        core_data = self._core_data.copy(order='F')
        core_data[self._core_mask] = np.fromiter(x, dtype=Float)
        sol_vector = np.asfortranarray(core_data)
        pert_cost = NetworkWithPerturbationsProblem._s_pert_function(
            self._pdata, self._size, self._y0, sol_vector,
            self._pcore, self.vector_map, self.vector_map_mask,
            NetworkProblem._s_ode_function
        )

        return (self._factor * pert_cost + cost,)

    def __get_deepcopy__(self):
        return NetworkWithPerturbationsProblem(dim=self.dimension)


class NetworkProblemFactory(LassimProblemFactory):
    """
    Factory class for NetworkProblem/NetworkWithPerturbationsProblem.
    Not really useful considering that the problem variables are global one.
    """

    def __init__(self, cost_data: Tuple[Vector, ...], y0: Vector,
                 ode_function: Callable[
                     [Vector, Vector, Vector, Vector, Vector, int], Vector],
                 pert_function: Callable[
                     [Vector, int, Vector, Vector, Vector, Vector, int,
                      Callable[[Vector, Vector, Vector, Vector, Vector, int],
                               Vector]], float],
                 pert_factor: float):
        NetworkProblem._s_ode_function = ode_function
        # divides data considering presence or not of perturbations data
        if len(cost_data) == 5:
            NetworkWithPerturbationsProblem._s_pert_core = cost_data[3]
            NetworkWithPerturbationsProblem._s_pert_data = cost_data[4]
            cost_data = (cost_data[0], cost_data[1], cost_data[2])
        NetworkProblem._s_cost_data = cost_data
        NetworkProblem._s_y0 = y0
        self.__is_pert = False
        if pert_function is not None:
            NetworkWithPerturbationsProblem._s_pert_function = pert_function
            NetworkWithPerturbationsProblem._s_pert_factor = pert_factor
            self.__is_pert = True

    @classmethod
    def new_instance(cls, cost_data: Tuple[Vector, ...], y0: Vector,
                     ode_function: Callable[
                         [Vector, Vector, Vector, Vector, Vector, int], Vector],
                     pert_function: Callable[
                         [Vector, int, Vector, Vector, Vector, Vector, int,
                          Callable[[Vector, Vector, Vector, Vector, Vector, int,
                                    Vector], Vector]], float] = None,
                     pert_factor: float = 0) -> 'NetworkProblemFactory':
        """
        Creates a new instance of a NetworkProblemFactory. Use this method
        instead of calling __init__ directly.

        :param cost_data: A tuple containing the data for the cost evaluation
            of the problem. The first three elements must be the peripheral
            data, the sigma and the time sequence. An optional forth and fifth
            values means the presence of perturbations data. Forth value is
            the perturbations of the core, fifth value is the perturbation of
            the peripheral gene.
        :param y0: Starting values for ODE evaluation.
        :param ode_function: Function for performing the ODE evaluation.
        :param pert_function: Function for evaluate the perturbations impact.
        :param pert_factor: The perturbations factor for perturbations impact.
        :return: An instance of a NetworkProblemFactory.
        """

        factory = NetworkProblemFactory(
            cost_data, y0, ode_function, pert_function, pert_factor
        )
        return factory

    def build(self, dim: int, bounds: Tuple[List[float], List[float]],
              vector_map: Tuple[Vector, ...], known_sol: List[Vector] = None,
              **kwargs) -> NetworkProblem:
        """
        Construct a NetworkProblem/NetworkWithPerturbationsProblem with the
        parameters passed in the factory instantiation.

        :param dim: Number of variables to optimize for the problem.
        :param bounds: Tuple with the list of lower bounds and upper bounds for
            each problem variable. Both list must have size equal to dim.
        :param vector_map: Tuple containing two vectors needed for the cost
            evaluation. Their values and their representation are independent
            from the problem.
        :param known_sol: List of known solutions for this problem. Useful for
            keeping trace of previously found solutions.
        :param kwargs: Extra values, must be present a key named 'core-data'
            containing a tuple of 2 Vector. The second vector must be a mask for
            the first one.
        :return: An instance of NetworkProblem/NetworkWithPerturbationsProblem.
        """

        NetworkProblem._s_dim = dim
        NetworkProblem._s_bounds = bounds
        NetworkProblem._s_map_tuple = vector_map
        NetworkProblem._s_core_data = kwargs["core_data"]
        if not self.__is_pert:
            return NetworkProblem(known_sol=known_sol)
        else:
            # TODO NetworkWithPerturbationsProblem
            raise Exception()
