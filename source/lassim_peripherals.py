import logging
import os
import subprocess
from typing import Tuple, List, Callable

import numpy as np
import pandas as pd
import sys
from PyGMO import topology
from sortedcontainers import SortedDict
from sortedcontainers import SortedList

from core.factories import OptimizationFactory
from core.functions.common_functions import odeint1e8_lassim
from core.functions.perturbation_functions import perturbation_peripheral
from core.handlers.csv_handlers import DirectoryCSVSolutionsHandler
from core.lassim_context import LassimContext, OptimizationArgs
from core.solutions.peripheral_solution import PeripheralSolution
from customs.configuration_custom import parse_peripherals_config, \
    default_terminal, peripheral_configuration_example
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
                    sec_args: List[OptimizationArgs]
                    ) -> Tuple[List[PeripheralSolution], List[str]]:
    # from the file corresponding to the core system, create the CoreSystem and
    # its values, then build the corresponding NetworkSystem
    network = create_network(files.network, core_files.core_system)
    core = network.core
    context = LassimContext(
        network, main_args, odeint1e8_lassim, perturbation_peripheral,
        PeripheralSolution, sec_args
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
        iter_function(core_data.values, core.num_tfacts, core.react_count)
    )
    headers = ["source", "lambda", "vmax"] + [tfact for tfact in core.tfacts]

    def dirname_creator(name: str) -> Callable[[SortedList, int], str]:
        # def wrapper(num_solutions: int, num_variables: int) -> str:
        #     return "{}_{}_vars_top{}".format(
        #         name, num_solutions, num_variables
        #     )
        return lambda x, y: "{}_{}_vars_top{}".format(
            name, x[0].number_of_variables, y
        )

    final_handler = DirectoryCSVSolutionsHandler(
        output.directory, float("inf"), headers
    )
    best_genes_solutions = []
    # may Kotlin and Java replace Python in the future
    # Python sucks, so I can't do this in parallel
    # optimize independently for each gene
    for gene, gene_data in peripherals_data_generator:

        prob_factory, start_problem = problem_setup(gene_data, context)
        PeripheralSolution._get_gene_name = lambda x: gene
        handler = DirectoryCSVSolutionsHandler(
            output.directory, output.num_solutions, headers,
            dirname_creator(gene)
        )

        optimization = optimization_builder.build(
            context, prob_factory, start_problem,
            SortedDict({gene: gene_data.reactions}),
            handler, logging.getLogger(__name__)
        )
        solutions = optimization.solve(topol=topology.ring())

        # save the best one in a gene specific directory
        final_handler.handle_solutions(solutions, "{}_best".format(gene))
        best_genes_solutions.append(solutions[0])
    return best_genes_solutions, headers


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
    list_config = [temp_config.format(i) for i in range(num_tasks)]
    list_files = [temp_file.format(i) for i in range(num_tasks)]
    for i in range(num_tasks):
        task_config = from_parser_to_builder(config, list_config[i])
        task_config.add_section("Input Data").add_key_value(
            "network", list_files[i]
        ).add_section("Output").add_key_value(
            "best result", list_files[i]
        ).add_section("Extra").add_key_value(
            "num tasks", str(1)
        ).build()
        network_subsets[i].to_csv(list_files[i], sep="\t", index=False)
    return list_files, list_config


def start_jobs(config_files: List[str]):
    # For each network file a new set of command line options must be created.
    # If a log file is used, maybe each process should have it independent
    # version.

    processes = []
    for config in config_files:
        python = sys.executable
        process = subprocess.Popen([
            python, os.path.join(os.getcwd(), "source/lassim_peripherals.py"),
            config
        ])
        processes.append(process)
    for process in processes:
        process.wait()


def merge_results(network_files: List[str], output: OutputFiles):
    results = []
    for file in network_files:
        results.append(pd.read_csv(file, sep="\t"))
    output_filename = os.path.join(output.directory, output.filename)
    merged_result = pd.concat(results, ignore_index=True)
    merged_result.to_csv(output_filename, sep="\t", index=False)
    logging.getLogger(__name__).info(
        "Generated file {}".format(output_filename)
    )


def cleaning_temps(config_files, network_files):
    for file in network_files:
        os.remove(file)
    for config_file in config_files:
        os.remove(config_file)


def lassim_peripherals():
    script_name = "lassim_peripherals"
    # read terminal arguments
    args = default_terminal(script_name, peripheral_configuration_example)

    # extra argument for this script are: name for output file
    config, files, core_files, output, main_args, sec_args, extra = \
        parse_peripherals_config(args)

    if extra.num_tasks == 1:
        solutions, headers = peripherals_job(
            files, core_files, output, main_args, sec_args
        )
        # each solution is the solution for a single gene.
        # merges them into a DataFrame and saves them into the network.csv
        # file for the main process.
        result = pd.concat([solution.get_solution_matrix(headers)
                            for solution in solutions],
                           ignore_index=True)
        result.to_csv(output.filename, sep="\t", index=False)
    else:
        network_files, config_files = prepare_peripherals_job(
            config, files, core_files, extra.num_tasks
        )
        start_jobs(config_files)
        merge_results(network_files, output)
        cleaning_temps(config_files, network_files)


if __name__ == '__main__':
    lassim_peripherals()
