from PyGMO import topology

from core.handlers.simple_csv_handler import SimpleCSVSolutionsHandler
from customs.core_creation import optimization_setup
from utilities.terminal import get_terminal_args, set_terminal_args

"""
This script and the functions used in it are a typical example of how the
toolbox works.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


def lassim():
    script_name = "lassim"

    # arguments from terminal are parsed
    files, output, opt_args = get_terminal_args(set_terminal_args(script_name))
    # the representation of the core to optimize and a builder of optimization
    # problems is returned
    core, builder = optimization_setup(files, opt_args)
    # list of headers that will be used in each solution
    headers = ["lambda", "vmax"] + [tfact for tfact in core.tfacts]
    handler = SimpleCSVSolutionsHandler(output[0], output[1], headers)
    # building of the optimization based on the parameters passed as arguments
    optimization = builder(handler, core, **opt_args.params)
    # list of solutions from solving the problem
    solutions = optimization.solve(
        n_islands=opt_args.num_islands, n_individuals=opt_args.num_individuals,
        topol=topology.ring()
    )
    final_handler = SimpleCSVSolutionsHandler(output[0], float("inf"), headers)
    final_handler.handle_solutions(solutions, "best_solutions.csv")


if __name__ == "__main__":
    lassim()
