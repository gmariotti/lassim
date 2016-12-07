import logging
from inspect import signature
from typing import Callable, Tuple, Optional

from PyGMO import topology, archipelago, island
from sortedcontainers import SortedDict, SortedList

from core.lassim_context import LassimContext, OptimizationArgs
from core.lassim_problem import LassimProblem, LassimProblemFactory
from core.solutions.lassim_solution import LassimSolution
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class BaseOptimization:
    """
    Base class representation of an Optimization. The method that must be
    implemented is the build method, used for building different instances of
    the same optimization object but with different parameters.
    """

    def __init__(self, algo,
                 iter_func: Callable[..., Tuple[Optional[LassimProblem],
                                                SortedDict, bool]]):
        self._algorithm = algo
        # can be None, remember it
        self._iterate = iter_func

        # these values will be set after a call to build
        # in this way is possible to instantiate this class multiple time
        # without having to change the iteration function and the algorithm
        self._prob_factory = None
        self._start_problem = None
        self._start_reactions = None
        self._context = None
        self._handler = None
        self._logger = None
        self._n_evolutions = 0
        self._n_islands = 0
        self._n_individuals = 0

    def build(self, context: LassimContext, prob_factory: LassimProblemFactory,
              start_problem: LassimProblem, reactions: SortedDict,
              handler: SolutionsHandler, logger: logging.Logger,
              **kwargs) -> 'BaseOptimization':
        """
        Used for building a BaseOptimization with the parameter passed in the
        __init__ call.
        :param context: A LassimContext instance. Its OptimizationArgs must
        contain the type of algorithm to use and the parameters needed.
        :param prob_factory: The factory for building new instances of the
        problem. At each iteration, it will be passed as argument of the
        iter_func if has been set.
        :param start_problem: The starting problem to solve.
        :param reactions: The map of reactions for this problem.
        :param handler: The SolutionsHandler instance for manage the list of
        solutions found in each iteration.
        :param logger: A logger for logging various optimization steps.
        :param kwargs: Use kwargs for extra value in extension class.
        :return: the BaseOptimization instance built from the parameter context.
        """
        new_instance = self.__class__(self._algorithm, self._iterate)
        new_instance._context = context
        new_instance._prob_factory = prob_factory
        new_instance._start_problem = start_problem
        new_instance._start_reactions = reactions
        new_instance._handler = handler
        new_instance._logger = logger

        # optimization setup
        opt_args = context.primary_first
        valid_params = self.handle_parameters(opt_args)
        if len(valid_params) > 0:
            # from a callable of the algorithm, the _algorithm property changes
            # to an instance of the algorithm
            new_instance._algorithm = new_instance._algorithm(**valid_params)
        else:
            new_instance._algorithm = new_instance._algorithm()
        new_instance._logger.info(str(new_instance._algorithm))

        # set the archipelago parameters
        new_instance._n_evolutions = opt_args.num_evolutions
        new_instance._n_islands = opt_args.num_islands
        new_instance._n_individuals = opt_args.num_individuals
        return new_instance

    def handle_parameters(self, opt_args: OptimizationArgs):
        """
        Evaluates which parameters in the OptimizationArgs instance are valid
        and which not for the algorithm set. Override this method if you want
        to dynamically change the parameters between each optimization cycle.
        :param opt_args: An instance of OptimizationArgs for testing the
        parameters.
        :return: A dictionary with just the valid parameters for the algorithm.
        """
        valid_params = signature(self._algorithm.__init__).parameters
        input_params = opt_args.params
        output_params = {name: input_params[name]
                         for name in input_params
                         if name in valid_params}
        return output_params

    def solve(self, topol=topology.unconnected(), **kwargs) -> SortedList:
        """
        Tries to solve this optimization problem by generating a list of
        BaseSolution ordered by their cost.
        :param topol: The topology to use for the archipelago. The default value
        is an unconnected topology.
        :param kwargs: Extra parameters, to be used for method override.
        :return: A SortedList of BaseSolution for this optimization problem.
        """
        solutions = SortedList()

        try:
            iteration = 1
            solution = self._generate_solution(
                self._start_problem, self._start_reactions, topol
            )
            solutions.add(solution)
            self._logger.info("({}) - New solution found.".format(iteration))

            # check that the iteration function has been set
            if self._iterate is not None:
                prob, reactions, do_iteration = self._iterate(
                    self._prob_factory, solution
                )
                while do_iteration:
                    solution = self._generate_solution(
                        prob, reactions, topol
                    )
                    solutions.add(solution)
                    iteration += 1
                    self._logger.info(
                        "({}) - New solution found.".format(iteration)
                    )
                    prob, reactions, do_iteration = self._iterate(
                        self._prob_factory, solution
                    )
            self._logger.info("BaseOptimization completed.")
        # FIXME - is horrible to have to catch all possible exceptions but
        # requires a bit of time to understand all the possible exceptions
        # that can be thrown.
        except Exception:
            self._logger.exception("Exception occurred during execution...")
        finally:
            self._logger.info("Returning solutions found.")
            return solutions

    def _generate_solution(self, prob: LassimProblem, reactions: SortedDict,
                           topol) -> LassimSolution:
        """
        Creates a new archipelago to solve the problem with the algorithm passed
        as argument, it solve it, pass the list of solutions to the handler and
        then returns the best solution found.
        :param prob: The LassimProblem instance to solve.
        :param reactions: The dictionary of reactions associated to the problem.
        :param topol: The topology of the archipelago.
        :return: The best solution found from the solving of the prob instance.
        """
        archi = self._generate_archipelago(prob, topol)
        archi.evolve(self._n_evolutions)
        archi.join()
        solutions = self._get_solutions(archi, prob, reactions)
        self._handler.handle_solutions(solutions)
        return solutions[0]

    def _generate_archipelago(self, prob: LassimProblem, topol) -> archipelago:
        """
        Generates a PyGMO.archipelago from an input problem and an input
        topology. The algorithm used is the one set at creation time.
        :param prob: The LassimProblem instance to solve.
        :param topol: The wanted topology for the archipelago.
        :return: The archipelago for solving the LassimProblem.
        """
        archi = archipelago(
            self._algorithm, prob, self._n_islands - 1, self._n_individuals,
            topology=topol
        )
        # this island is used to add previous champions to the archipelago
        # population
        isl = island(self._algorithm, prob, self._n_individuals)
        prev_champions = prob.champions
        i = 0
        while i < self._n_individuals and i < len(prev_champions):
            isl.set_x(i, prev_champions[i].x)
            i += 1
        # adds the island only if any previous champion was present
        archi.push_back(isl)
        return archi

    def _get_solutions(self, archi: archipelago, prob: LassimProblem,
                       reactions: SortedDict) -> SortedList:
        """
        From a PyGMO.archipelago, generates the list of best solutions created
        from each island, constructing each solution using the class reference
        in the context instance.
        :param archi: The PyGMO.archipelago instance from which extracting the
        solution of each island.
        :param prob: The LassimProblem that has been solved by archi.
        :param reactions: The map of reactions specific for this solution.
        """
        champions = [isl.population.champion for isl in archi]
        solutions = SortedList(
            [self._context.SolutionClass(champ, reactions, prob)
             for champ in champions]
        )
        return solutions

    def print(self):
        raise NotImplementedError(self.print.__name__)
