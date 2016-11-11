from logging import Logger
from typing import Callable, Dict

import psutil
from PyGMO import topology, archipelago
from sortedcontainers import SortedDict, SortedList

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
    Base class representation of an Optimization. The method that must be
    implemented is the build method, used for building different instances of
    the same optimization object but with different parameters.
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
        self._evolutions = 0
        self._algorithm = None

    def build(self, handler: SolutionsHandler, core: CoreSystem,
              **kwargs) -> 'BaseOptimization':
        raise NotImplementedError(self.build.__name__)

    def solve(self, n_islands: int, n_individuals: int,
              topol=topology.unconnected()) -> SortedList:
        solutions = SortedList()

        try:
            iteration = 1
            solution = self.__generate_solution(
                self._start_problem, self._start_reactions, n_individuals,
                n_islands, topol
            )
            solutions.add(solution)
            self._logger.info("({}) - New solution found.".format(iteration))

            problem, reactions, do_iteration = self._iterate(
                self._probl_factory, solution
            )
            while do_iteration:
                solution = self.__generate_solution(
                    problem, reactions, n_individuals, n_islands, topol
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
        except Exception:
            self._logger.exception("Exception occurred during solution...")
            self._logger.error("Returning solutions found so far")
        return solutions

    def __generate_solution(self, problem: LassimProblem, reactions: SortedDict,
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
        archi.evolve(self._evolutions)
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
        solutions = SortedList(
            [Solution(champ, reactions, (prob.vector_map, prob.vector_map_mask))
             for champ in champions]
        )
        self._handler.handle_solutions(solutions)
        return solutions[0]

    def print(self):
        raise NotImplementedError(self.print.__name__)


class OptimizationArgs:
    """
    This class represents the list of arguments for an optimization. Except for
    the number of cores, each argument is read-only and is initialized at class
    instantiation.
    """

    def __init__(self, opt_type: str, params: Dict, num_cores: int,
                 evolutions: int, individuals: int, pert_factor: float):
        self.__type = opt_type
        self.__params = params
        self.__cores = num_cores
        self.__islands = self.__cores
        self.__evolutions = evolutions
        self.__individuals = individuals
        self.__pert_factor = pert_factor

    @property
    def type(self) -> str:
        return self.__type

    @property
    def params(self) -> Dict:
        return self.__params

    @property
    def num_cores(self) -> int:
        return self.__cores

    @num_cores.setter
    def num_cores(self, num_cores: int):
        self.__cores = num_cores
        # if the number is less than one, then use all the CPUs available
        if num_cores < 1:
            self.__cores = psutil.cpu_count
        self.__islands = num_cores

    @property
    def num_islands(self) -> int:
        return self.__islands

    @property
    def num_evolutions(self) -> int:
        return self.__evolutions

    @property
    def num_individuals(self) -> int:
        return self.__individuals

    @property
    def pert_factor(self) -> float:
        return self.__pert_factor

    def log_args(self, logger: Logger, is_pert: bool = False):
        """
        Used to log the optimization arguments inserted by the user.
        :param logger: the logging object to use
        :param is_pert: if the presence of the perturbations factor has to be
        logged or not.
        """
        logger.info("Algorithm used is {}".format(self.__type))
        logger.info("Number of cores is {}".format(self.__cores))
        logger.info("Number of evolutions for archipelago is {}".format(
            self.__evolutions
        ))
        logger.info("Number of individuals for each island is {}".format(
            self.__individuals
        ))
        if is_pert:
            logger.info("Perturbations factor is {}".format(self.__pert_factor))
