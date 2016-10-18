from copy import deepcopy
from typing import Tuple, Callable, List

import numpy as np
from PyGMO.problem import base

from utilities.type_aliases import Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class CoreProblem(base):
    """
    This class is a representation of the optimization problem of a core in
    a network. It is completely independent on how the equations system is
    designed.
    """

    def __init__(self, dim: int, bounds: Tuple[List[float], List[float]],
                 cost_data: Tuple[Vector, Vector, Vector],
                 map_tuple: Tuple[Vector, Vector],
                 y0: Vector, ode_function: Callable[
                [Vector, Vector, Tuple[Vector, Vector, Vector, int]], Vector
            ]):
        # dim is the number of variables to optimize
        super(CoreProblem, self).__init__(dim)

        # only arguments that should be public
        self.vector_map, self.vector_map_mask = map_tuple

        # TODO - validity check on data?
        # set parameters for objective function
        self._data, self._sigma, self._time = cost_data
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
        solution_vector = np.fromiter(x, dtype=np.float64)

        results = self._ode_function(
            self._y0, self._time,
            (solution_vector, self.vector_map, self.vector_map_mask, self._size)
        )
        norm_results = results / np.amax(results, axis=0)
        cost = np.sum(np.power((self._data - norm_results) / self._sigma, 2))

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


class CoreProblemFactory:
    """
    Factory class for getting a reference to a building function used to create
    multiple instances of a CoreProblem, or CoreWithKnockProblem, with a set of
    standard data.
    """

    def __init__(self, cost_data: Tuple, y0: Vector, ode_function: Callable[
        [Vector, Vector, Tuple[Vector, Vector, Vector, int]], Vector
    ]):
        self._ode_func = ode_function
        self._cost_data = cost_data
        self._y0 = y0

    @classmethod
    def new_instance(cls, cost_data: Tuple, y0: Vector, ode_function: Callable[
        [Vector, Vector, Tuple[Vector, Vector, Vector, int]], Vector
    ]) -> 'CoreProblemFactory':
        factory = CoreProblemFactory(cost_data, y0, ode_function)
        return factory

    def build(self, dim: int, bounds: Tuple[List[float], List[float]],
              reactions: Tuple[Vector, Vector]) -> CoreProblem:
        if len(self._cost_data) == 3:
            # problem without knock data
            return CoreProblem(
                dim, bounds, self._cost_data, reactions,
                self._y0, self._ode_func
            )
        elif len(self._cost_data) == 4:
            # problem with knock data TODO
            raise NotImplementedError("Knock data problem not yet implemented")
        else:
            raise RuntimeError("Number of elements in cost_data is not valid")
