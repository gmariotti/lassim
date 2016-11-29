import logging
from typing import Dict, Callable, NamedTuple, List

import numpy as np
from sortedcontainers import SortedDict

from core.base_optimization import BaseOptimization
from core.core_problem import CoreProblemFactory
from core.core_system import CoreSystem
from core.factories import OptimizationFactory
from core.lassim_context import OptimizationArgs, LassimContext
from core.utilities.type_aliases import Vector, Float, Tuple4V
from customs.core_functions import default_bounds, generate_reactions_vector, \
    iter_function
from data_management.csv_format import parse_network, parse_time_sequence, \
    parse_network_data, parse_perturbations_data

"""
Set of custom functions for creation of the core and its optimization builder.
Can be considered an example of possible integration of the source/core module
in an already existing pipeline.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


def create_core(network_file: str) -> CoreSystem:
    """
    Creates a CoreSystem instance and logs it by reading the name of the network
    file given as input.
    :param network_file: Path of the file containing the network.
    :return: An instance of the CoreProblem.
    """
    tf_network = parse_network(network_file)
    core = CoreSystem(tf_network)
    logging.getLogger(__name__).info("\n" + str(core))
    return core


def problem_setup(files: Dict[str, str], context: LassimContext,
                  data_class: Callable[..., NamedTuple]
                  ) -> (NamedTuple, CoreProblemFactory):
    """
    It setups the core problem factory for constructing core problems.
    :param files: List of files path containing the data. Must be a dictionary
    with the following keys: data, time and, optionally, perturbations.
    :param context: a LassimContext instance.
    :param data_class: A callable object that returns a namedtuple as output.
    The data that takes as input must be the data, sigma, times, perturbations
    and y0, all of them np.ndarray.
    :return: A tuple with the namedtuple containing the data and an instance
    of the problem factory.
    """
    data, sigma, times, y0 = data_parsing(files)
    is_pert_prob, perturbations = data_parse_perturbations(files, context.core)

    # creation of the correct type of problem to solve
    if is_pert_prob:
        problem_builder = CoreProblemFactory.new_instance(
            (data, sigma, times, perturbations), y0,
            context.ode, context.perturbation,
        )
        logging.getLogger(__name__).info(
            "Created builder for problem with perturbations."
        )
    else:
        problem_builder = CoreProblemFactory.new_instance(
            (data, sigma, times), y0, context.ode
        )
        logging.getLogger(__name__).info(
            "Created builder for problem without perturbations."
        )
    return data_class(data, sigma, times, perturbations, y0), problem_builder


def data_parsing(files: Dict[str, str]) -> Tuple4V:
    """
    Generate the set of data used in the optimization from the file name
    :param files: Dictionary with the filenames containing the data
    :return: Vector for mean of data, standard deviation, time series and
    starting values at t0
    """
    time_seq = parse_time_sequence(files["time"])
    data_list = [parse_network_data(data_file) for data_file in files["data"]]

    np_data_list = [
        np.array([value for key, value in data.items()], dtype=Float)
        for data in data_list
        ]
    data_maxes = [np.amax(data, axis=1) for data in np_data_list]
    maxes = np.array(data_maxes, dtype=Float)
    real_maxes = np.amax(maxes, axis=0)
    np_data_norm = [(data.T / real_maxes).T for data in np_data_list]
    data_mean_n = np.array(np_data_norm, dtype=Float).mean(axis=0)
    # unbiased, divisor is N - 1
    std_dev = np.std(np.array(np_data_norm, dtype=Float), axis=2)

    data_mean = np.array(np_data_list, dtype=Float).mean(axis=0)

    return data_mean_n.T, std_dev.mean(axis=0), time_seq, data_mean.T[0].copy()


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
        # FIXME - perfect case for Optional.
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
    except OSError:
        logging.getLogger(__name__).error("File {} doesn't exist.".format(
            files["perturbations"]
        ))
        return False, np.empty(0)


def optimization_setup(core: CoreSystem, problem_builder: CoreProblemFactory,
                       main_args: List[OptimizationArgs],
                       sec_args: List[OptimizationArgs]) -> BaseOptimization:
    """
    Setup of a BaseOptimization instance, constructing the problem using the
    input CoreSystem, the CoreProblemFactory and the OptimizationArgs.
    For the problem bounds is used the custom.core_functions.default_bounds
    function while for the vector map and its mask the
    custom.core_functions.generate_reactions_vector.
    :param core: An instance representing the CoreSystem to optimize.
    :param problem_builder: A CoreProblemFactory for building the corresponding
    problem to solve.
    :param main_args: The list of optimization algorithms for the main
    optimization.
    :param sec_args: The, optional, list of algorithms for a second optimization
    process. [!] not implemented yet.
    :return: The BaseOptimization class to use for building the instance that
    will solve the problem.
    """
    reactions_ids = SortedDict(core.from_reactions_to_ids())

    # depending on the secondary arguments, a different optimization instance
    # is created
    main_opt = main_args[0]
    problem = problem_builder.build(
        dim=(core.num_tfacts * 2 + core.react_count),
        bounds=default_bounds(core.num_tfacts, core.react_count),
        vector_map=generate_reactions_vector(reactions_ids),
        pert_factor=main_opt.pert_factor
    )

    if len(sec_args) == 1:
        raise NotImplementedError(
            "Secondary algorithm are not been implemented yet. Sorry :("
        )
        # opt_builder = OptimizationFactory.new_multistart_optimization(
        #     main_opt.type, problem_builder, problem, reactions_ids,
        #     iter_function, sec_args[0].type
        # )
    elif len(sec_args) == 0:
        opt_builder = OptimizationFactory.new_base_optimization(
            main_opt.type, problem_builder, problem, reactions_ids,
            iter_function
        )
    else:
        raise RuntimeError("How the hell did you get there?!")
    return opt_builder
