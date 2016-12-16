import logging
from argparse import ArgumentParser
from collections import namedtuple
from typing import Callable, NamedTuple, Iterable, Tuple, List, Dict

import numpy as np
from PyGMO import topology
from sortedcontainers import SortedDict

from core.functions.common_functions import odeint1e8_lassim
from core.functions.perturbation_functions import perturbation_func_sequential
from core.handlers.composite_handler import CompositeSolutionsHandler
from core.handlers.csv_handlers import SimpleCSVSolutionsHandler
from core.handlers.plot_handler import PlotBestSolutionsHandler
from core.lassim_context import LassimContext, OptimizationArgs
from core.solutions.lassim_solution import LassimSolution
from core.utilities.type_aliases import Tuple3V
from customs.core_creation import create_core, problem_setup, \
    optimization_setup
from utilities.logger_setup import LoggerSetup
from utilities.terminal import set_files_args, set_core_optimization_args, \
    set_logger_args, set_output_args, get_logger_args, get_files_args, \
    get_output_args, get_core_optimization_args

"""
This script and the functions used in it are how the toolbox works.
Use this script as an inspiration to integrate the core module into your
pipeline.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.1"


def lassim_core_terminal(script_name: str
                         ) -> Tuple[Dict[str, str], Tuple[str, int],
                                    List[OptimizationArgs],
                                    List[OptimizationArgs]]:
    parser = ArgumentParser(script_name)
    # set terminal arguments
    set_files_args(parser)
    set_core_optimization_args(parser)
    set_logger_args(parser)
    set_output_args(parser)

    # get terminal arguments
    setup = LoggerSetup()

    # retrieve input from terminal
    args = parser.parse_args()
    get_logger_args(args, setup)
    files, is_pert = get_files_args(args)
    output = get_output_args(args)
    core_args = get_core_optimization_args(args)

    logger = logging.getLogger(__name__)
    logger.info("Logging Core Optimization arguments")
    for core_arg in core_args:
        core_arg.log_args(logger, is_pert)

    return files, output, core_args, list()


def data_producer(context: LassimContext, data_tuple: NamedTuple
                  ) -> Callable[[LassimSolution], Iterable[Tuple3V]]:
    ode_function = context.ode
    y0 = data_tuple.y0
    time = data_tuple.times
    data = data_tuple.data
    result = np.empty(y0.size)

    def wrapper(solution: LassimSolution) -> Iterable[Tuple3V]:
        results = ode_function(
            y0, time, solution.solution_vector, solution.react_vect,
            solution.react_mask, y0.size, result
        )
        norm_results = results / np.amax(results, axis=0)
        for i in range(0, y0.size):
            yield data[:, i], norm_results[:, i], time

    return wrapper


def lassim_core():
    script_name = "lassim_core"

    # arguments from terminal are parsed
    files, output, main_args, sec_args = lassim_core_terminal(script_name)
    core = create_core(files["network"])
    # create a context for solving this problem
    context = LassimContext(
        core, main_args, odeint1e8_lassim, perturbation_func_sequential,
        LassimSolution, sec_args
    )
    # get a namedtuple with the data parsed and the factory for the problem
    # construction
    # TODO - consider adding it to the context
    DataTuple = namedtuple(
        "DataTuple", ["data", "sigma", "times", "perturb", "y0"]
    )
    data, p_factory = problem_setup(files, context, DataTuple)
    base_builder, start_problem = optimization_setup(
        context.core, p_factory, context.primary_opts, context.secondary_opts
    )

    # construct the solutions handlers for managing the solution of each
    # optimization step

    # list of headers that will be used in each solution
    tfacts = [tfact for tfact in core.tfacts]
    headers = ["lambda", "vmax"] + tfacts
    csv_handler = SimpleCSVSolutionsHandler(output[0], output[1], headers)
    axis = [("time", "[{}]".format(name)) for name in tfacts]
    plot_handler = PlotBestSolutionsHandler(
        output[0], tfacts, axis, data_producer(context, data)
    )
    handler = CompositeSolutionsHandler([csv_handler, plot_handler])
    # building of the optimization based on the parameters passed as arguments
    optimization = base_builder.build(
        context, p_factory, start_problem,
        SortedDict(core.from_reactions_to_ids()), handler,
        logging.getLogger(__name__)
    )
    # list of solutions from solving the problem
    solutions = optimization.solve(topol=topology.ring())
    final_handler = SimpleCSVSolutionsHandler(output[0], float("inf"), headers)
    final_handler.handle_solutions(solutions, "best_solutions.csv")


if __name__ == "__main__":
    lassim_core()
