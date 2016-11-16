from PyGMO import topology

from core.functions.common_functions import odeint1e8_lassim
from core.functions.perturbation_functions import perturbation_func_sequential
from core.handlers.simple_csv_handler import SimpleCSVSolutionsHandler
from core.lassim_context import LassimContext
from core.solutions.lassim_solution import LassimSolution
from customs.core_creation import create_core, problem_setup, \
    optimization_setup
from utilities.terminal import get_terminal_args, set_terminal_args

"""
This script and the functions used in it are how the toolbox works.
Use this script as an inspiration to integrate the core module into your
pipeline.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


def lassim():
    script_name = "lassim"

    # arguments from terminal are parsed
    files, output, opt_args = get_terminal_args(set_terminal_args(script_name))
    core = create_core(files["network"])
    # create a context for solving this problem
    context = LassimContext(
        core, opt_args, odeint1e8_lassim, perturbation_func_sequential,
        LassimSolution
    )
    # get a namedtuple with the data parsed and the factory for the problem
    # construction
    data, p_factory = problem_setup(files, context)
    builder = optimization_setup(context.core, p_factory, context.opt_args)

    # construct the solutions handlers for managing the solution of each
    # optimization step

    # list of headers that will be used in each solution
    headers = ["lambda", "vmax"] + [tfact for tfact in core.tfacts]
    handler = SimpleCSVSolutionsHandler(output[0], output[1], headers)
    # building of the optimization based on the parameters passed as arguments
    optimization = builder(context, handler)
    # list of solutions from solving the problem
    solutions = optimization.solve(
        n_islands=opt_args.num_islands, n_individuals=opt_args.num_individuals,
        topol=topology.ring()
    )
    final_handler = SimpleCSVSolutionsHandler(output[0], float("inf"), headers)
    final_handler.handle_solutions(solutions, "best_solutions.csv")


if __name__ == "__main__":
    lassim()
