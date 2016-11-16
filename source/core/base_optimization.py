from typing import Callable

from PyGMO import topology, archipelago, island
from sortedcontainers import SortedDict, SortedList

from core.lassim_context import LassimContext
from core.lassim_problem import LassimProblem, LassimProblemFactory
from core.solutions.lassim_solution import LassimSolution
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
                 problem: LassimProblem, reactions: SortedDict, evolutions: int,
                 iter_func: Callable[..., bool]):
        self._probl_factory = prob_factory
        self._start_problem = problem
        self._start_reactions = reactions
        self._iterate = iter_func
        self._context = None
        self._handler = None
        self._logger = None
        self._evolutions = evolutions
        self._algorithm = None

    def build(self, context: LassimContext, handler: SolutionsHandler,
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
        finally:
            return solutions

    def __generate_solution(self, problem: LassimProblem, reactions: SortedDict,
                            n_individuals: int, n_threads: int, topol
                            ) -> LassimSolution:
        """
        Creates a new archipelago to solve the problem with the DE algorithm.
        It returns the best solution found after the optimization process.
        """
        archi = archipelago(
            self._algorithm, problem, n_threads, n_individuals,
            topology=topol
        )
        # try to add islands with previously found best solutions
        for pchamp in problem.champions:
            isl = island(self._algorithm, problem, n_individuals)
            isl.set_x(0, pchamp.x)
            archi.push_back(isl)
        archi.evolve(self._evolutions)
        archi.join()
        # FIXME
        # self._archipelagos.append(archi)
        solution = self.__get_best_solution(
            archi, problem, reactions
        )
        return solution

    # not side-effect free but at least I isolated it
    def __get_best_solution(self, archi: archipelago, prob: LassimProblem,
                            reactions: SortedDict) -> LassimSolution:
        """
        From an archipelago, generates the list of the best solutions for
        each island. Then, it pass them to the instance of SolutionHandler and
        returns the best one.
        """
        champions = [isl.population.champion for isl in archi]
        solutions = SortedList(
            [self._context.SolutionClass(champ, reactions, prob)
             for champ in champions]
        )
        self._handler.handle_solutions(solutions)
        return solutions[0]

    def print(self):
        raise NotImplementedError(self.print.__name__)
