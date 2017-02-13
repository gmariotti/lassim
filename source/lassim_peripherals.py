import logging
from typing import Tuple, List, Callable

import numpy as np
import pandas as pd
from PyGMO import topology

from core.factories import OptimizationFactory
from core.functions.common_functions import odeint1e8_lassim
from core.functions.perturbation_functions import perturbation_peripherals
from core.handlers.csv_handlers import DirectoryCSVSolutionsHandler
from core.lassim_context import LassimContext, OptimizationArgs
from core.solutions.lassim_solution import LassimSolution
from customs.configuration_custom import peripherals_terminal
from customs.peripherals_creation import create_network, problem_setup, \
    parse_peripherals_data
from customs.peripherals_functions import iter_function
from data_management.csv_format import parse_core_data
from utilities.configuration import ConfigurationParser, from_parser_to_builder
from utilities.data_classes import OutputFiles, InputFiles, CoreFiles

"""
Main script for handling the peripherals problem in the Lassim Toolbox.
Can also be used as an example on how the toolbox works and how the core module
can be integrated in an existing pipeline.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def peripherals_job(files: InputFiles, core_files: CoreFiles,
                    output: OutputFiles, main_args: List[OptimizationArgs],
                    sec_args: List[OptimizationArgs]):
    # from the file corresponding to the core system, create the CoreSystem and
    # its values, then build the corresponding NetworkSystem
    network = create_network(files.network, core_files.core_system)
    core = network.core
    context = LassimContext(
        network, main_args, odeint1e8_lassim, perturbation_peripherals,
        LassimSolution, sec_args
    )
    # parse the peripherals data just once, in order to improve the performance
    # and return a dictionary of <gene:DataTuple> to use for starting the
    # peripherals optimization
    core_data = parse_core_data(core_files.core_system)
    peripherals_data_generator = parse_peripherals_data(
        network, files, core_files, core_data
    )
    optimization_builder = OptimizationFactory.new_base_optimization(
        context.primary_first.type,
        iter_function(core_data, core.num_tfacts, core.react_count)
    )
    headers = ["lambda", "vmax"] + [tfact for tfact in core.tfacts]

    def dirname_creator(name: str) -> Callable[[int, int], str]:
        # def wrapper(num_solutions: int, num_variables: int) -> str:
        #     return "{}_{}_vars_top{}".format(
        #         name, num_solutions, num_variables
        #     )
        return lambda x, y: "{}_{}_vars_top{}".format(name, x, y)

    # optimize independently for each gene
    # Python sucks, so I can't do this in parallel
    # may Kotlin and Java replace Python in the future
    for gene, gene_data in peripherals_data_generator:

        prob_factory, start_problem = problem_setup(gene_data, context)

        handler = DirectoryCSVSolutionsHandler(
            output.directory, output.num_solutions, headers,
            dirname_creator(gene)
        )

        optimization = optimization_builder.build(
            context, prob_factory, start_problem, gene_data.reactions,
            handler, logging.getLogger(__name__)
        )
        solutions = optimization.solve(topol=topology.ring())
        # TODO - handler for final solution
        # save the best one in a gene specific directory


def prepare_peripherals_job(config: ConfigurationParser, files: InputFiles,
                            core_files: CoreFiles, num_tasks: int
                            ) -> Tuple[List[str], List[str]]:
    # try to parse the network file for seeing if everything works
    network = create_network(files.network, core_files.core_system)

    # for each task, the configuration changes only in the network file.
    # Hidden files are used for the partial network and the specific ini.
    network_frame = pd.read_csv(files.network, sep="\t")
    temp_file = ".lassim_hidden_temp_peripherals_{}.csv"
    temp_config = ".lassim_hidden_temp_config_{}.ini"
    network_subsets = np.array_split(network_frame, num_tasks)
    list_config = [temp_config.format(i) for i in range(0, num_tasks)]
    list_files = [temp_file.format(i) for i in range(0, num_tasks)]
    for i in range(num_tasks):
        task_config = from_parser_to_builder(config, list_config[i])
        task_config.add_section("Input Data").add_key_value(
            "network", list_files[i]
        ).build()
        network_subsets[i].to_csv(list_files[i], sep="\t", index=False)
    return list_files, list_config


def start_jobs(network_files: List[str], config_files: List[str]):
    # For each network file a new set of command line options must be created.
    # If a log file is used, maybe each process should have it independent
    # version.

    # process = subprocess.Popen([commands])
    # process.wait()
    # for each best directory, take the best file and merge it with the best
    # from the other genes
    pass


def lassim_peripherals():
    script_name = "lassim_peripherals"
    # read terminal arguments
    # extra argument for this script are: name for output file
    config, files, core_files, output, main_args, sec_args, extra = \
        peripherals_terminal(script_name)

    if extra.num_tasks == 1:
        peripherals_job(files, core_files, output, main_args, sec_args)
    else:
        network_files, config_files = prepare_peripherals_job(
            config, files, core_files, extra.num_tasks
        )
        start_jobs(network_files, config_files)
        # TODO - merge
        # TODO - cleaning


if __name__ == '__main__':
    lassim_peripherals()
