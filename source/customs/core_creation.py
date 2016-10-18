import pprint
from typing import Dict

import numpy as np
from PyGMO import topology
from sortedcontainers import SortedDict

from core.base_optimization import BaseOptimization, OptimizationArgs
from core.core_problem import CoreProblemFactory
from core.core_system import CoreSystem
from core.factories import OptimizationFactory
from core.handlers.simple_csv_handler import SimpleCSVSolutionsHandler
from core.ode_functions import odeint1e8_function
from core.serializers.csv_serializer import CSVSerializer
from customs.core_functions import default_bounds, generate_reactions_vector, \
    iter_function
from data_management.csv_format import parse_network, parse_time_sequence, \
    parse_patient_data
from utilities.type_aliases import Vector, Float

"""
Set of custom functions for creation and optimization of the core.
Can be considered an example of typical use of the toolbox.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


def optimization_setup(files: Dict[str, str], opt_args: OptimizationArgs,
                       serializer: CSVSerializer,
                       ) -> (BaseOptimization, SimpleCSVSolutionsHandler):
    # core construction
    # custom, just for this case
    core = create_core(files["network"])

    files_tuple = data_parsing(files)

    reactions_ids = SortedDict(core.from_reactions_to_ids())
    # creation of the problem to solve
    problem_builder = CoreProblemFactory.new_instance(
        files_tuple, np.zeros(core.get_tfacts_num()), odeint1e8_function
    )
    problem = problem_builder.build(
        dim=(core.get_tfacts_num() * 2 + core.react_count),
        bounds=default_bounds(core.get_tfacts_num(), core.react_count),
        reactions=generate_reactions_vector(reactions_ids),
    )
    opt_builder = OptimizationFactory.new_optimization_instance(
        opt_args.type, problem_builder, (problem, reactions_ids),
        opt_args.evolutions, iter_function
    )

    # handler construction
    handler = create_handler(core, serializer)

    optimization = opt_builder(
        handler, core, **opt_args.params
    )

    return optimization, handler


def optimization_run(optimization: BaseOptimization, num_islands: int,
                     handler: SimpleCSVSolutionsHandler):
    solutions = optimization.solve(n_threads=num_islands, n_individuals=10,
                                   topol=topology.ring())
    handler.handle_solutions(solutions, "best_solutions.csv")


def create_core(network_file: str):
    tf_network = parse_network(network_file)
    core = CoreSystem(tf_network)

    # TODO - debug
    core.print()
    return core


def data_parsing(files: Dict[str, str]) -> (Vector, Vector, Vector):
    """
    Generate the set of data used in the optimization from the file name
    :param files: Dictionary with the filenames containing the data
    :return: ndarray for each file
    """
    time_seq = parse_time_sequence(files["time"])
    data_mean = parse_patient_data(files["data"])
    sigma = parse_patient_data(files["sigma"])

    # TODO - think how to put them outside of here
    data_mean = np.array([value for key, value in data_mean.items()],
                         dtype=Float).T
    sigma = np.array([value for key, value in sigma.items()],
                     dtype=Float).T

    # TODO - debug
    pprint.pprint(time_seq)
    pprint.pprint(data_mean)
    pprint.pprint(sigma)
    return data_mean, sigma, time_seq


def create_handler(core, serializer):
    headers = ["lambda", "vmax"]
    headers += core.tfacts
    serializer.set_headers(headers)
    handler = SimpleCSVSolutionsHandler(serializer)
    return handler
