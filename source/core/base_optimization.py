import logging
from inspect import signature
from typing import Callable

from PyGMO import topology, archipelago, island
from sortedcontainers import SortedDict, SortedList

from core.lassim_context import LassimContext, OptimizationArgs
from core.lassim_problem import LassimProblem, LassimProblemFactory
from core.solutions.lassim_solution import LassimSolution
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class BaseOptimization:
    """
    Base class representation of an Optimization. The method that must be
    implemented is the build method, used for building different instances of
    the same optimization object but with different parameters.
    """

    def __init__(self, algo, prob_factory: LassimProblemFactory,
                 problem: LassimProblem, reactions: SortedDict,
                 iter_func: Callable[..., bool]):
        self._algorithm = algo
        self._probl_factory = prob_factory
        self._start_problem = problem
        self._start_reactions = reactions
        self._iterate = iter_func

        # this value will be set after a call to build
        self._context = None
        self._handler = None
        self._logger = None
        self._n_evolutions = 0
        self._n_islands = 0
        self._n_individuals = 0

    def build(self, context: LassimContext, handler: SolutionsHandler,
              logger: logging.Logger, **kwargs) -> 'BaseOptimization':
        """

        :param context:
        :param handler:
        :param logger:
        :param kwargs: Use kwargs for extra value in extension class
        :return:
        """
        opt_args = context.opt_args
        valid_parameters = self.handle_parameters(opt_args)
        logger.info("Optimization parameters are\n{}".format(valid_parameters))
        algo = self._algorithm(**valid_parameters)
        new_instance = BaseOptimization(
            algo, self._probl_factory, self._start_problem,
            self._start_reactions, self._iterate
        )
        new_instance._context = context
        new_instance._handler = handler
        new_instance._logger = logger
        # set the archipelago parameters
        new_instance._n_evolutions = opt_args.num_evolutions
        new_instance._n_islands = opt_args.num_islands
        new_instance._n_individuals = opt_args.num_individuals
        return new_instance

    def handle_parameters(self, opt_args: OptimizationArgs):
        valid_params = signature(self._algorithm.__init__).parameters
        input_params = opt_args.params
        output_params = {
            name: input_params[name]
            for name in input_params
            if name in valid_params
        }
        return output_params

    def solve(self, topol=topology.unconnected()) -> SortedList:
        solutions = SortedList()

        try:
            iteration = 1
            solution = self._generate_solution(
                self._start_problem, self._start_reactions, topol
            )
            solutions.add(solution)
            self._logger.info("({}) - New solution found.".format(iteration))

            problem, reactions, do_iteration = self._iterate(
                self._probl_factory, solution
            )
            while do_iteration:
                solution = self._generate_solution(
                    problem, reactions, topol
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

    def _generate_solution(self, problem: LassimProblem, reactions: SortedDict,
                           topol) -> LassimSolution:
        """
        Creates a new archipelago to solve the problem with the DE algorithm.
        It returns the best solution found after the optimization process.
        """
        archi = archipelago(
            self._algorithm, problem, self._n_islands, self._n_individuals,
            topology=topol
        )
        # try to add islands with previously found best solutions
        for pchamp in problem.champions:
            isl = island(self._algorithm, problem, self._n_individuals)
            isl.set_x(0, pchamp.x)
            archi.push_back(isl)
        archi.evolve(self._n_evolutions)
        archi.join()
        # FIXME
        # self._archipelagos.append(archi)
        solution = self._get_best_solution(
            archi, problem, reactions
        )
        return solution

    # not side-effect free but at least I isolated it
    def _get_best_solution(self, archi: archipelago, prob: LassimProblem,
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
