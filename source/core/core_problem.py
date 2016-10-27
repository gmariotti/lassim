from copy import deepcopy
from typing import Tuple, Callable, List

import numpy as np

from core.lassim_problem import LassimProblem, LassimProblemFactory
from utilities.type_aliases import Vector, Float, Tuple2V, Tuple3V

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class CoreProblem(LassimProblem):
    """
    This class is a representation of the optimization problem of a core in
    a network. It is completely independent on how the equations system is
    designed.
    """

    def __init__(self, dim: int, bounds: Tuple[List[float], List[float]],
                 cost_data: Tuple3V,
                 map_tuple: Tuple2V,
                 y0: Vector, ode_function: Callable[
                [Vector, Vector, Tuple[Vector, Vector, Vector, int]], Vector
            ]):
        # dim is the number of variables to optimize
        super(CoreProblem, self).__init__(dim)

        # only arguments that should be public
        self.vector_map, self.vector_map_mask = map_tuple
        if self.vector_map.shape != self.vector_map_mask.shape:
            raise ValueError(
                "Map shape {} is different from mask shape {}".format(
                    self.vector_map.shape, self.vector_map_mask.shape
                ))

        # set parameters for objective function
        self._data, self._sigma, self._time = cost_data

        # check that data and sigma are compatible
        try:
            np.broadcast(self._data, self._sigma)
        except ValueError:
            raise ValueError(
                "Data shape {} is incompatible with sigma shape {}".format(
                    self._data.shape, self._sigma.shape
                ))
        self._sigma2 = np.power(self._sigma, 2)

        self._y0 = y0
        self._size = y0.size

        self._ode_function = ode_function

        # sets lower bounds and upper bounds
        self.set_bounds(bounds[0], bounds[1])
        # saves a copy for __get_deepcopy__
        self._bounds = bounds

    def _objfun_impl(self, x):
        """
        Calculates the objective function for this problem
        :param x: Tuple containing the value of each parameter to optimize
        :return: A tuple of a single value, containing the cost
        """
        solution_vector = np.fromiter(x, dtype=Float)

        results = self._ode_function(
            self._y0, self._time,
            (solution_vector, self.vector_map, self.vector_map_mask, self._size)
        )
        # FIXME - handle the case in which one of the value in np.amax(results)
        # is 0, in order to avoid 0/0 = nan case
        norm_results = results / np.amax(results, axis=0)
        # cost = np.sum(np.power((self._data - norm_results) / self._sigma, 2))
        cost = np.sum(np.power((self._data - norm_results), 2) / self._sigma2)

        return (cost,)

    def __get_deepcopy__(self):
        copy = CoreProblem(
            dim=self.dimension, bounds=deepcopy(self._bounds),
            cost_data=(self._data, self._sigma, self._time),
            map_tuple=(self.vector_map.copy(), self.vector_map_mask.copy()),
            y0=self._y0.copy(), ode_function=self._ode_function
        )
        return copy

    def __deepcopy__(self, memodict={}):
        return self.__get_deepcopy__()

    def __copy__(self):
        return self.__get_deepcopy__()


class CoreWithPerturbationsProblem(CoreProblem):
    def __init__(self, dim: int, bounds: Tuple[List[float], List[float]],
                 cost_data: Tuple3V, map_tuple: Tuple2V, y0: Vector,
                 ode_function: Callable[
                     [Vector, Vector,
                      Tuple[Vector, Vector, Vector, int]], Vector
                 ],
                 pert_function: Callable[
                     [Vector, int, Vector,
                      Tuple[Vector, Vector, Vector, int],
                      Callable[[Vector, Vector, Vector, Vector], float]], float
                 ],
                 pert_data: Vector, pert_factor: float):
        super(CoreWithPerturbationsProblem, self).__init__(
            dim, bounds, cost_data, map_tuple, y0, ode_function
        )
        self._pert_function = pert_function

        # the perturbation data should be already formatted for the perturbation
        # function in order to make the problem as general as possible
        self._pert_data = pert_data
        self._factor = pert_factor

    def _objfun_impl(self, x):
        # TODO - cost and pert_cost are assumed independent from each other
        # possible improvement can be to run one of them asynchronously
        cost = super(CoreWithPerturbationsProblem, self)._objfun_impl(x)[0]
        sol_vector = np.fromiter(x, dtype=Float)
        pert_cost = self._pert_function(
            self._pert_data, self._size, self._y0,
            (sol_vector, self.vector_map, self.vector_map_mask, self._size),
            self._ode_function
        )

        # tested on ipython - float factor seems faster than a np.ndarray of one
        # element
        return (self._factor * pert_cost + cost,)

    def __get_deepcopy__(self):
        copy = CoreWithPerturbationsProblem(
            dim=self.dimension, bounds=deepcopy(self._bounds),
            cost_data=(self._data, self._sigma, self._time),
            map_tuple=(self.vector_map.copy(), self.vector_map_mask.copy()),
            y0=self._y0.copy(), ode_function=self._ode_function,
            pert_function=self._pert_function, pert_data=self._pert_data,
            pert_factor=self._factor
        )
        return copy


class CoreProblemFactory(LassimProblemFactory):
    """
    Factory class for getting a reference to a building function used to create
    multiple instances of a CoreProblem, or CoreWithPerturbationsProblem, with a
    set of standard data.
    """

    def __init__(self, cost_data: Tuple, y0: Vector, ode_function: Callable[
        [Vector, Vector, Tuple[Vector, Vector, Vector, int]], Vector
    ], pert_function: Callable[
        [Vector, int, Vector, Tuple[Vector, Vector, Vector, int],
         Callable[[Vector, Vector, Vector], Vector]], float
    ], pert_factor: float):
        self._ode_func = ode_function
        self._pert_func = pert_function
        # divides data considering presence or not of perturbations data
        if len(cost_data) == 4:
            self._pert_data = cost_data[3]
            cost_data = (cost_data[0], cost_data[1], cost_data[2])
        self._cost_data = cost_data
        self._y0 = y0
        self._pert_factor = pert_factor

    @classmethod
    def new_instance(cls, cost_data: Tuple, y0: Vector, ode_function: Callable[
        [Vector, Vector, Tuple[Vector, Vector, Vector, int]], Vector
    ], pert_function: Callable[
        [Vector, int, Vector, Tuple[Vector, Vector, Vector, int],
         Callable[[Vector, Vector, Vector], Vector]], float
    ] = None, pert_factor: float = 0) -> 'CoreProblemFactory':
        factory = CoreProblemFactory(
            cost_data, y0, ode_function, pert_function, pert_factor
        )
        return factory

    def build(self, dim: int, bounds: Tuple[List[float], List[float]],
              vector_map: Tuple2V) -> CoreProblem:
        if len(self._cost_data) == 3:
            if self._pert_func is None:
                return CoreProblem(
                    dim, bounds, self._cost_data, vector_map,
                    self._y0, self._ode_func
                )
            else:
                return CoreWithPerturbationsProblem(
                    dim, bounds, self._cost_data, vector_map,
                    self._y0, self._ode_func,
                    self._pert_func, self._pert_data, self._pert_factor
                )
        else:
            raise RuntimeError("Number of elements in cost_data is not valid")
