from typing import Tuple, Callable, List

import numpy as np

from core.lassim_problem import LassimProblem, LassimProblemFactory
from core.utilities.type_aliases import Vector, Float, Tuple2V

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class CoreProblem(LassimProblem):
    """
    This class is a representation of an optimization problem for solving a
    core problem. It is completely independent on how the equations system is
    designed and solved.
    For compatibility purposes, the _s_ variables must be set before the
    creation of the problem. This is needed for extending a PyGMO.problem.base
    class and avoid exceptions during execution.
    [!] NOT THREAD SAFE
    """

    _s_dim = 0
    _s_bounds = ([], [])
    _s_cost_data = (np.empty(1), np.empty(1), np.empty(1))
    _s_map_tuple = (np.empty(1), np.empty(1))
    _s_y0 = np.empty(1)
    _s_ode_function = None

    def __init__(self, dim: int = 1, known_sol: List[Vector] = None):
        """
        Constructor of a CoreProblem.

        :param dim: not used, present just for avoiding PyGMO crashes. Use
            instead _s_dim for the problem dimension.
        :param known_sol: List of known solutions previously found. They seems
            to not help for speeding the optimization process, use them as a
            comparison with the optimization results.
        """

        # dim is the number of variables to optim ize
        super(CoreProblem, self).__init__(CoreProblem._s_dim)

        # for numpy exp overflow
        np.seterr(over="ignore")

        # only arguments that should be public
        self.vector_map, self.vector_map_mask = CoreProblem._s_map_tuple
        if self.vector_map.shape != self.vector_map_mask.shape:
            raise ValueError(
                "Map shape {} is different from mask shape {}".format(
                    self.vector_map.shape, self.vector_map_mask.shape
                ))

        # set parameters for objective function
        self._data, self._sigma, self._time = CoreProblem._s_cost_data
        self._y0 = CoreProblem._s_y0

        # check that data and sigma are compatible
        try:
            np.broadcast(self._data, self._sigma)
        except ValueError:
            raise ValueError(
                "Data shape {} is incompatible with sigma shape {}".format(
                    self._data.shape, self._sigma.shape
                ))
        self._sigma2 = np.power(self._sigma, 2)
        self._size = CoreProblem._s_y0.size

        # sets lower bounds and upper bounds
        self.set_bounds(CoreProblem._s_bounds[0], CoreProblem._s_bounds[1])

        # these variables are used for performance efficiency
        self._result_mem = np.empty(self._size)
        self._cost_mem = np.empty(self._data.shape)

        # sets the best known solutions
        if known_sol is not None:
            self.best_x = [vector.tolist() for vector in known_sol]

    def _objfun_impl(self, x):
        """
        Calculates the objective function for this problem with x as decision
        vector.

        :param x: Tuple containing the value of each parameter to optimize.
        :return: A tuple of a single value, containing the cost for this value
            of x.
        """

        solution_vector = np.fromiter(x, dtype=Float)
        results = CoreProblem._s_ode_function(
            self._y0, self._time, solution_vector,
            self.vector_map, self.vector_map_mask, self._size, self._result_mem
        )
        norm_results = np.divide(results, np.amax(results, axis=0))
        cost = np.sum(np.divide(np.power(
            np.subtract(self._data, norm_results), 2, out=self._cost_mem),
            self._sigma2, out=self._cost_mem)
        )

        return (cost,)

    def __get_deepcopy__(self):
        return CoreProblem(dim=self.dimension)

    def __deepcopy__(self, memodict={}):
        return self.__get_deepcopy__()

    def __copy__(self):
        return self.__get_deepcopy__()


class CoreWithPerturbationsProblem(CoreProblem):
    """
    This class is an extension of the CoreProblem taking also into account the
    presence of perturbations data.
    For compatibility purposes, the _s_ variables must be set before the
    creation of the problem. This is needed for extending a PyGMO.problem.base
    class and avoid exceptions during execution.
    [!] NOT THREAD SAFE
    """

    _s_pert_function = None
    _s_pert_data = np.empty(1)
    _s_pert_factor = 0

    def __init__(self, dim: int = 1, known_sol: List[Vector] = None):
        """
        Constructor of a CoreWithPerturbationsProblem.

        :param dim: not used, present just for avoiding PyGMO crashes. Use
            instead _s_dim for the problem dimension.
        :param known_sol: List of known solutions previously found. They seems
            to not help for speeding the optimization process, use them as a
            comparison with the optimization results.
        """

        # the perturbation data should be already formatted for the perturbation
        # function in order to make the problem as general as possible
        self._pdata = CoreWithPerturbationsProblem._s_pert_data
        self._factor = CoreWithPerturbationsProblem._s_pert_factor
        super(CoreWithPerturbationsProblem, self).__init__(
            CoreProblem._s_dim, known_sol
        )

    def _objfun_impl(self, x):
        """
        Calculates the objective function for this problem with x as decision
        vector.

        :param x: Tuple containing the value of each parameter to optimize.
        :return: A tuple of a single value, containing the cost for this value
            of x plus the influence of the perturbations data times the
            perturbation cost.
        """

        # cost and pert_cost are assumed independent from each other but running
        # them asynchronously with a pool is slower than doing that sequentially
        cost = super(CoreWithPerturbationsProblem, self)._objfun_impl(x)[0]
        sol_vector = np.asfortranarray(np.fromiter(x, dtype=Float))
        pert_cost = CoreWithPerturbationsProblem._s_pert_function(
            self._pdata, self._size, self._s_y0,
            sol_vector, self.vector_map, self.vector_map_mask,
            CoreProblem._s_ode_function
        )

        # tested on ipython - float factor seems faster than a np.ndarray of one
        # element
        return (self._factor * pert_cost + cost,)

    def __get_deepcopy__(self):
        return CoreWithPerturbationsProblem(dim=self.dimension)


class CoreProblemFactory(LassimProblemFactory):
    """
    Factory class for constructing CoreProblem or CoreWithPerturbationsProblem.
    Must be instantiated with a call to new_instance.
    """

    def __init__(self, cost_data: Tuple[Vector, ...], y0: Vector,
                 ode_function: Callable[
                     [Vector, Vector, Vector, Vector, Vector, int], Vector],
                 pert_function: Callable[
                     [Vector, int, Vector, Vector, Vector, Vector, int,
                      Callable[[Vector, Vector, Vector, Vector, Vector, int],
                               Vector]], float],
                 pert_factor: float):
        CoreProblem._s_ode_function = ode_function
        # divides data considering presence or not of perturbations data
        if len(cost_data) == 4:
            CoreWithPerturbationsProblem._s_pert_data = cost_data[3]
            cost_data = (cost_data[0], cost_data[1], cost_data[2])
        CoreProblem._s_cost_data = cost_data
        CoreProblem._s_y0 = y0
        self.__is_pert = False
        if pert_function is not None:
            CoreWithPerturbationsProblem._s_pert_function = pert_function
            CoreWithPerturbationsProblem._s_pert_factor = pert_factor
            self.__is_pert = True

    @classmethod
    def new_instance(cls, cost_data: Tuple[Vector, ...], y0: Vector,
                     ode_function: Callable[
                         [Vector, Vector, Vector, Vector, Vector, int], Vector],
                     pert_function: Callable[
                         [Vector, int, Vector, Vector, Vector, Vector, int,
                          Callable[[Vector, Vector, Vector, Vector, Vector, int,
                                    Vector], Vector]], float] = None,
                     pert_factor: float = 0) -> 'CoreProblemFactory':
        """
        Builds a factory for the generation of
        CoreProblem/CoreWithPerturbationsProblem instances with the parameters
        passed as arguments.

        :param cost_data: Tuple containing the vectors for the cost evaluation.
            The first three elements must be the data, the sigma and the time
            sequence. An optional forth value means the presence of
            perturbations data.
        :param y0: Starting values for ODE evaluation.
        :param ode_function: Function for performing the ODE evaluation.
        :param pert_function: Function for evaluate the perturbations impact.
        :param pert_factor: The perturbations factor for perturbations impact.
        :return: An instance of a CoreProblemFactory.
        """

        factory = CoreProblemFactory(
            cost_data, y0, ode_function, pert_function, pert_factor
        )
        return factory

    def build(self, dim: int, bounds: Tuple[List[float], List[float]],
              vector_map: Tuple2V, known_sol: List[Vector] = None,
              **kwargs) -> CoreProblem:
        """
        Construct a CoreProblem/CoreWithPerturbationsProblem with the parameters
        passed in the factory instantiation.

        :param dim: Number of variables to optimize for the problem.
        :param bounds: Tuple with the list of lower bounds and upper bounds for
            each problem variable. Both list must have size equal to dim.
        :param vector_map: Tuple containing two vectors needed for the cost
            evaluation. Their values and their representation are independent
            from the problem.
        :param known_sol: List of known solutions for this problem. Useful for
            keeping trace of previously found solutions.
        :param kwargs: Optional extra values, not used here. Used them in
            CoreProblemFactory subclasses.
        :return: An instance of a CoreProblem/CoreWithPerturbationsProblem.
        """

        CoreProblem._s_dim = dim
        CoreProblem._s_bounds = bounds
        CoreProblem._s_map_tuple = vector_map
        if not self.__is_pert:
            return CoreProblem(known_sol=known_sol)
        else:
            return CoreWithPerturbationsProblem(known_sol=known_sol)
