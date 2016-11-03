import logging
from typing import Dict

import numpy as np
from PyGMO import topology
from sortedcontainers import SortedDict

from core.base_optimization import BaseOptimization, OptimizationArgs
from core.core_problem import CoreProblemFactory
from core.core_system import CoreSystem
from core.factories import OptimizationFactory
from core.functions.ode_functions import odeint1e8_function
from core.functions.perturbation_functions import perturbation_func_sequential
from core.handlers.simple_csv_handler import SimpleCSVSolutionsHandler
from core.serializers.csv_serializer import CSVSerializer
from core.solutions_handler import SolutionsHandler
from customs.core_functions import default_bounds, generate_reactions_vector, \
    iter_function
from data_management.csv_format import parse_network, parse_time_sequence, \
    parse_network_data, parse_perturbations_data
from utilities.type_aliases import Vector, Float

"""
Set of custom functions for creation and optimization of the core.
Can be considered an example of typical use of the toolbox.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


def optimization_setup(files: Dict[str, str], opt_args: OptimizationArgs,
                       serializer: CSVSerializer,
                       ) -> (BaseOptimization, SimpleCSVSolutionsHandler):
    # core construction
    # custom, just for this case
    core = create_core(files["network"])

    files_tuple = data_parsing(files)
    is_pert_prob, perturbations = data_parse_perturbations(files, core)

    reactions_ids = SortedDict(core.from_reactions_to_ids())

    # starting values are the data values at time 0
    y0 = files_tuple[0][0]

    # creation of the correct type of problem to solve
    if is_pert_prob:
        problem_builder = CoreProblemFactory.new_instance(
            (*files_tuple, perturbations), y0,
            odeint1e8_function, perturbation_func_sequential,
            opt_args.pert_factor
        )
        logging.getLogger(__name__).info(
            "Created builder for problem with perturbations."
        )
    else:
        problem_builder = CoreProblemFactory.new_instance(
            files_tuple, y0, odeint1e8_function
        )
        logging.getLogger(__name__).info(
            "Created builder for problem without perturbations."
        )
    problem = problem_builder.build(
        dim=(core.num_tfacts * 2 + core.react_count),
        bounds=default_bounds(core.num_tfacts, core.react_count),
        vector_map=generate_reactions_vector(reactions_ids),
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
                     num_individuals: int, handler: SimpleCSVSolutionsHandler):
    solutions = optimization.solve(
        n_threads=num_islands, n_individuals=num_individuals,
        topol=topology.ring()
    )
    handler.handle_solutions(solutions, "best_solutions.csv")


def create_core(network_file: str) -> CoreSystem:
    tf_network = parse_network(network_file)
    core = CoreSystem(tf_network)
    logging.getLogger(__name__).info(core)
    return core


def data_parsing(files: Dict[str, str]) -> (Vector, Vector, Vector):
    """
    Generate the set of data used in the optimization from the file name
    :param files: Dictionary with the filenames containing the data
    :return: Vector for mean of data, standard deviation and time series
    """
    time_seq = parse_time_sequence(files["time"])
    data_list = [parse_network_data(data_file) for data_file in files["data"]]

    np_data_list = [
        np.array([value for key, value in data.items()], dtype=Float).T
        for data in data_list
        ]
    data_mean = np.array(np_data_list, dtype=Float).mean(axis=0)
    # unbiased, divisor is N - 1
    std_dev = np.std(np.array(np_data_list, dtype=Float), ddof=1, axis=0)

    return data_mean, std_dev.mean(axis=0), time_seq


def data_parse_perturbations(files: Dict[str, str], core: CoreSystem
                             ) -> (bool, Vector):
    """
    Parse the data for perturbations if they are present. If they are presents,
    checks that their size corresponds to the number of transcription factors
    expected in the core.
    :param files: dictionary with, or without, a reference to a "perturbations"
    file.
    :param core: CoreSystem object
    :return: True and parsed data if they are present and valid, False and empty
    vector if not.
    """
    try:
        is_present = False
        pert_file = files["perturbations"]
        pert_data = parse_perturbations_data(pert_file)
        # checks data validity
        # checks if data shape is >= to (#tfacts, #tfacts)
        num_tfacts = core.num_tfacts
        if pert_data.shape >= (num_tfacts, num_tfacts):
            tfacts_pert_data = pert_data[:, :num_tfacts]
            # now checks if the data shape of data related to the transcription
            # factors is equal or not to (#tfacts, #tfacts)
            if tfacts_pert_data.shape == (num_tfacts, num_tfacts):
                is_present = True
            else:
                pert_data = np.empty(0)
        else:
            pert_data = np.empty(0)

        return is_present, pert_data
    except KeyError:
        return False, np.empty(0)


def create_handler(core: CoreSystem, serializer) -> SolutionsHandler:
    headers = ["lambda", "vmax"]
    headers += core.tfacts
    serializer.set_headers(headers)
    handler = SimpleCSVSolutionsHandler(serializer)
    return handler
