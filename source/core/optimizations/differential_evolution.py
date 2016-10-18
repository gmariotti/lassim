import logging
from inspect import signature
from typing import Callable, Dict, Tuple

from PyGMO import algorithm, topology, archipelago
from sortedcontainers import SortedDict, SortedList, SortedListWithKey

from core.base_optimization import BaseOptimization
from core.core_problem import CoreProblem, CoreProblemFactory
from core.core_system import CoreSystem
from core.solution import Solution
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class DEOptimization(BaseOptimization):
    """
    Represents an implementation of the BaseOptimization class for the
    Differential Evolution algorithms offered by PyGMO.algorithm
    """

    type_name = "Differential Evolution"

    def __init__(self, prob_factory: CoreProblemFactory,
                 problem: Tuple[CoreProblem, SortedDict], evolutions: int,
                 iter_func: Callable[..., bool]):
        super(DEOptimization, self).__init__(prob_factory, problem, iter_func)
        # default settings for algorithm
        self._algorithm = algorithm.de()
        self._logger = logging.getLogger(__name__)
        self._evol = evolutions

    def build(self, handler: SolutionsHandler, core: CoreSystem,
              **kwargs) -> 'DEOptimization':
        de_opt = DEOptimization(
            self._probl_factory, self._start_problem, self._evol, self._iterate
        )
        valid_args = self.verify_arguments(**kwargs)
        if len(valid_args) > 0:
            de_opt._algorithm = algorithm.de(**valid_args)
            de_opt._logger.info("Arguments for {} are:\n{}".format(
                self.type_name, valid_args
            ))
        de_opt._handler = handler
        de_opt._core = core
        return de_opt

    def verify_arguments(self, **kwargs) -> Dict:
        arguments = signature(algorithm.de.__init__).parameters
        valid_found = {}
        for arg in arguments:
            if arg in kwargs:
                valid_found[arg] = kwargs[arg]
        return valid_found

    def solve(self, n_threads: int, n_individuals: int,
              topol=topology.unconnected()) -> SortedList:
        solutions = SortedListWithKey(key=Solution.get_cost)

        try:
            iteration = 1
            solution = self._generate_solution(
                self._start_problem, n_individuals, n_threads, topol
            )
            solutions.add(solution)
            self._logger.info("({}) - New solution found.".format(iteration))

            problem, do_iteration = self._iterate(self._probl_factory, solution)
            while do_iteration:
                solution = self._generate_solution(
                    problem, n_individuals, n_threads, topol
                )
                solutions.add(solution)
                iteration += 1
                self._logger.info(
                    "({}) - New solution found.".format(iteration))
                problem, do_iteration = self._iterate(self._probl_factory,
                                                      solution)
            self._logger.info("Differential evolution completed.")
        # FIXME - is horrible to have to catch all possible exceptions but
        # requires a bit of time to understand all the possible exceptions
        # that can be thrown.
        except:
            self._logger.exception("Exception occurred during solution...")
            self._logger.error("Returning solutions found so far")
        return solutions

    def _generate_solution(self, problem: Tuple[CoreProblem, SortedDict],
                           n_individuals: int, n_threads: int, topol
                           ) -> Solution:
        """
        Creates a new archipelago to solve the problem with the DE algorithm.
        It returns the best solution found after the optimization process.
        """
        archi = archipelago(
            self._algorithm, problem[0], n_threads, n_individuals,
            topology=topol
        )
        archi.evolve(self._evol)
        archi.join()
        solution = self._get_best_solution(
            archi, problem
        )
        return solution

    # not side-effect free but at least I isolated it
    def _get_best_solution(self, archi: archipelago,
                           prob: Tuple[CoreProblem, SortedDict]) -> Solution:
        """
        From an archipelago, generates the list of with the best solution for
        each island, pass them to an instance of SolutionHandler and then
        returns the best one.
        """
        champions = [isl.population.champion for isl in archi]
        solutions = SortedListWithKey(
            [Solution(champ, prob[1],
                      (prob[0].vector_map, prob[0].vector_map_mask))
             for champ in champions],
            key=Solution.get_cost
        )
        self._handler.handle_solutions(solutions)
        return solutions[0]

    def print(self):
        super(DEOptimization, self).print()
