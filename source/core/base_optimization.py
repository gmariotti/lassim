from logging import Logger
from typing import Callable, Tuple, Dict

import psutil
from PyGMO import topology, archipelago
from sortedcontainers import SortedDict, SortedList, SortedListWithKey

from core.core_system import CoreSystem
from core.lassim_problem import LassimProblem, LassimProblemFactory
from core.solution import Solution
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class BaseOptimization:
    """
    Represents the base class to implement for realizing a new optimization.
    Still undecided if iteration must go there or not.
    """

    def __init__(self, prob_factory: LassimProblemFactory,
                 problem: LassimProblem, reactions: SortedDict,
                 iter_func: Callable[..., bool]):
        self._probl_factory = prob_factory
        self._start_problem = problem
        self._start_reactions = reactions
        self._iterate = iter_func
        self._handler = None
        self._core = None
        self._logger = None
        self._evol = 0
        self._algorithm = None

    def build(self, handler: SolutionsHandler, core: CoreSystem, evols: int,
              **kwargs) -> 'BaseOptimization':
        raise NotImplementedError(self.build.__name__)

    def solve(self, n_threads: int, n_individuals: int,
              topol=topology.unconnected()) -> SortedList:
        solutions = SortedListWithKey(key=Solution.get_cost)

        try:
            iteration = 1
            solution = self._generate_solution(
                self._start_problem, self._start_reactions, n_individuals,
                n_threads, topol
            )
            solutions.add(solution)
            self._logger.info("({}) - New solution found.".format(iteration))

            problem, reactions, do_iteration = self._iterate(
                self._probl_factory, solution
            )
            while do_iteration:
                solution = self._generate_solution(
                    problem, reactions, n_individuals, n_threads, topol
                )
                solutions.add(solution)
                iteration += 1
                self._logger.info(
                    "({}) - New solution found.".format(iteration)
                )
                problem, reactions, do_iteration = self._iterate(
                    self._probl_factory, solution
                )
            self._logger.info("Differential evolution completed.")
        # FIXME - is horrible to have to catch all possible exceptions but
        # requires a bit of time to understand all the possible exceptions
        # that can be thrown.
        except:
            self._logger.exception("Exception occurred during solution...")
            self._logger.error("Returning solutions found so far")
        return solutions

    def _generate_solution(self, problem: LassimProblem, reactions: SortedDict,
                           n_individuals: int, n_threads: int, topol
                           ) -> Solution:
        """
        Creates a new archipelago to solve the problem with the DE algorithm.
        It returns the best solution found after the optimization process.
        """
        archi = archipelago(
            self._algorithm, problem, n_threads, n_individuals,
            topology=topol
        )
        archi.evolve(self._evol)
        archi.join()
        # FIXME
        # self._archipelagos.append(archi)
        solution = self._get_best_solution(
            archi, problem, reactions
        )
        return solution

    # not side-effect free but at least I isolated it
    def _get_best_solution(self, archi: archipelago, prob: LassimProblem,
                           reactions: SortedDict) -> Solution:
        """
        From an archipelago, generates the list of with the best solution for
        each island, pass them to an instance of SolutionHandler and then
        returns the best one.
        """
        champions = [isl.population.champion for isl in archi]
        # FIXME - test it because seems like that the worst solution is taken
        solutions = SortedListWithKey(
            [Solution(champ, reactions, (prob.vector_map, prob.vector_map_mask))
             for champ in champions],
            key=Solution.get_cost
        )
        self._handler.handle_solutions(solutions)
        return solutions[0]

    def print(self):
        raise NotImplementedError(self.print.__name__)


class OptimizationArgs:
    def __init__(self, opt_type: str, params: Dict, num_cores: int,
                 evolutions: int, individuals: int, pert_factor: float):
        self.type = opt_type
        self.params = params
        self._num_cores = num_cores
        # if the number is less than one, then use all the CPUs available
        if self._num_cores < 1:
            self._num_cores = psutil.cpu_count()
        self.num_islands = self._num_cores
        self.evolutions = evolutions
        self.individuals = individuals
        self.pert_factor = pert_factor

    def log_args(self, logger: Logger, is_pert: bool = False):
        """
        Used to log the optimization arguments inserted by the user.
        :param logger: the logging object to use
        :param is_pert: if the presence of the perturbations factor has to be
        logged or not.
        """
        logger.info("Algorithm used is {}".format(self.type))
        logger.info("Number of cores is {}".format(self._num_cores))
        logger.info("Number of evolutions for archipelago is {}".format(
            self.evolutions
        ))
        logger.info("Number of individuals for each island is {}".format(
            self.individuals
        ))
        if is_pert:
            logger.info("Perturbations factor is {}".format(self.pert_factor))
