import json
import logging
import os
from argparse import ArgumentParser
from typing import Dict, Tuple, List

import psutil

from core.factories import OptimizationFactory
from core.lassim_context import OptimizationArgs
from utilities.logger_setup import LoggerSetup

"""
This scripts contains all the possible terminal options of the user. Each
script from the toolbox should set the options that it needs and get them
from the terminal.
It should be improved with using subcommands instead of independent scripts.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

messages = {
    # MANDATORY
    "input-network": "The file path of the transcription factors network.",
    "input-data": "The files path of the data to analyze. Expected at least "
                  "two files",
    "time-series": "The file path of the time series in which the data where "
                   "collected.",
    "input-core": "The file path of the data related to an existing core",
    "number-of-cpus": "The number of CPUs available for use. Default is {}",

    # OPTIONAL
    # OPTIMIZATION
    "opt-type": "Type of optimization algorithm to use.  Look at PyGMO "
                "algorithms documentation for the list of valid parameters for "
                "each algorithm. Choices are {}.",
    "opt-json": "JSON file with the parameters for the optimization algorithm.",
    "cores": "Number of cores/islands used for the optimization process. "
             "Default for this system is {}.",
    "evolutions": "Number of evolutions for each archipelago. Default is {}.",
    "individuals": "Number of individuals used in the optimization algorithm "
                   "Default is {}.",
    "pert-factor": "Indicates the importance of the perturbations in the "
                   "objective function of the problem to solve. Must be a value"
                   " between 0 and 1. Default is {}.",
    "input-pert": "The file path of the perturbations file.",
    "sec-opt": "Similar to -o, but the algorithm is for a secondary "
               "optimization.",
    "sec-json": "Similar to -p, but for the secondary algorithm.",
    "sec-cores": "Similar to -c, but for the secondary algorithm.",
    "sec-evolutions": "Similar to -e, but for the secondary algorithm.",
    "sec-individuals": "Similar to -i, but for the secondary algorithm.",

    # GENERAL
    "log": "Sets the name of the file where to save the logs other than on "
           "screen.",
    "verbosity": "Increase verbosity of logs with INFO too.",
    "output-dir": "Name of directory for output files.",
    "number-of-solutions": "For each iteration, number of solutions to save."
}

default = {
    "cores": psutil.cpu_count(),
    "evolutions": 1,
    "individuals": 1,
    "pert-factor": 0
}


def set_core_files_args(parser: ArgumentParser):
    group = parser.add_argument_group("input data core")
    group.add_argument("inputN", metavar="input-network",
                       help=messages["input-network"])
    group.add_argument("inputD", metavar="input-data", nargs="+",
                       help=messages["input-data"])
    group.add_argument("inputT", metavar="time-series",
                       help=messages["time-series"])


def get_core_files_args(args) -> Tuple[Dict[str, str], bool]:
    logger = logging.getLogger(__name__)
    if not os.path.isfile(args.inputN):
        logger.error("File {} doesn't exist".format(args.inputN))
        exit(0)
    if len(args.inputD) < 2:
        logger.error("Expected two or more input files for data")
        exit(0)
    for input_file in args.inputD:
        if not os.path.isfile(input_file):
            logger.error("File {} doesn't exist".format(args.inputD))
            exit(0)
    if not os.path.isfile(args.inputT):
        logger.error("File {} doesn't exist".format(args.inputT))
        exit(0)

    files = {
        "network": args.inputN,
        "data": args.inputD,
        "time": args.inputT,
    }
    pert_file = getattr(args, "perturbations")
    if pert_file is not None and not os.path.isfile(pert_file):
        logger.error("File {} doesn't exist.".format(pert_file))
        exit(0)
    logger.info("Network file is {}".format(args.inputN))
    logger.info("Data file are {}".format(", ".join(args.inputD)))
    logger.info("Time series file is {}".format(args.inputT))

    is_pert = False
    if pert_file is not None:
        logger.info("Perturbations file is {}".format(pert_file))
        files["perturbations"] = pert_file
        is_pert = True

    return files, is_pert


def set_peripherals_files_args(parser: ArgumentParser):
    group = parser.add_argument_group("input data peripherals")
    group.add_argument("inputC", metavar="input-core",
                       help=messages["input-core"])
    group.add_argument("inputD", metavar="input-data", nargs="+",
                       help=messages["input-data"])
    group.add_argument("inputT", metavar="time-series",
                       help=messages["time-series"])
    group.add_argument("CPUs", metavar="num", type=int,
                       help=messages["number-of-cpus"].format(
                           default["cores"]
                       ))


def get_peripherals_files_args(parser: ArgumentParser):
    pass


def set_main_optimization_args(parser: ArgumentParser):
    group = parser.add_argument_group("main optimization")
    group.add_argument("-o", "--optimization", metavar="type",
                       choices=OptimizationFactory.labels_cus(),
                       default=OptimizationFactory.cus_default(),
                       help=messages["opt-type"].format(
                           ", ".join(OptimizationFactory.labels_cus())
                       ))
    group.add_argument("-p", "--parameters", metavar="json",
                       help=messages["opt-json"])
    group.add_argument("-c", "--cores", metavar="num",
                       default=default["cores"], type=int,
                       help=messages["cores"].format(default["cores"]))
    group.add_argument("-e", "--evolutions", metavar="num",
                       default=default["evolutions"], type=int,
                       help=messages["evolutions"].format(
                           default["evolutions"]
                       ))
    group.add_argument("-i", "--individuals", metavar="num",
                       default=default["individuals"], type=int,
                       help=messages["individuals"].format(
                           default["individuals"]
                       ))
    group.add_argument("--perturbations-factor", metavar="num",
                       default=default["pert-factor"], type=float,
                       help=messages["pert-factor"].format(
                           default["pert-factor"]
                       ))
    group.add_argument("--perturbations", metavar="file",
                       help=messages["input-pert"])


def get_main_optimization_args(args) -> List[OptimizationArgs]:
    algorithm = args.optimization
    params = {}
    param_filename = args.parameters
    if param_filename is not None and os.path.isfile(param_filename):
        with open(param_filename) as params_json:
            params = json.load(params_json)

    # get cores - checks if the user puts 0 or less. In this case uses the
    # default number in this system
    cores = args.cores
    if cores <= 0:
        cores = default["cores"]

    evols = args.evolutions
    if evols <= 0:
        evols = default["evolutions"]

    individuals = args.individuals
    if individuals <= 0:
        individuals = default["individuals"]

    pert_factor = getattr(args, "perturbations_factor")
    if pert_factor < 0 or pert_factor > 1:
        pert_factor = default["pert-factor"]

    return [OptimizationArgs(
        algorithm, params, cores, evols, individuals, pert_factor
    )]


def set_secondary_optimization_args(parser: ArgumentParser):
    # group for secondary optimization
    group = parser.add_argument_group("secondary optimization")
    group.add_argument("--secOptimization", metavar="type",
                       choices=OptimizationFactory.labels_cus(),
                       default=None,
                       help=messages["sec-opt"].format(
                           ", ".join(OptimizationFactory.labels_cus())
                       ))
    group.add_argument("--secParameters", metavar="json",
                       help=messages["sec-json"])
    group.add_argument("--secCores", metavar="num",
                       default=default["cores"], type=int,
                       help=messages["sec-cores"].format(default["cores"]))
    group.add_argument("--secEvolutions", metavar="num",
                       default=default["evolutions"], type=int,
                       help=messages["sec-evolutions"].format(
                           default["evolutions"]
                       ))
    group.add_argument("--secIndividuals", metavar="num",
                       default=default["individuals"], type=int,
                       help=messages["sec-individuals"].format(
                           default["individuals"]
                       ))


def get_secondary_args(args) -> List[OptimizationArgs]:
    algorithm = args.secOptimization
    # if the secondary algorithm is not set, there's no need to check for other
    # input parameters
    if algorithm is None:
        return []

    # check the json file with the list of parameters
    params = {}
    param_filename = args.secParameters
    if param_filename is not None and os.path.isfile(param_filename):
        with open(param_filename) as params_json:
            params = json.load(params_json)
    cores = args.secCores
    if cores <= 0:
        cores = default["cores"]

    evols = args.secEvolutions
    if evols <= 0:
        evols = default["evolutions"]

    individuals = args.secIndividuals
    if individuals <= 0:
        individuals = default["individuals"]

    return [OptimizationArgs(
        algorithm, params, cores, evols, individuals, default["pert-factor"]
    )]


def set_logger_args(parser: ArgumentParser):
    group = parser.add_argument_group("log options")
    group.add_argument("-l", "--log", metavar="file",
                       help=messages["log"])
    group.add_argument("-v", "--verbosity", action="store_true",
                       help=messages["verbosity"])


def get_logger_args(args, setup: LoggerSetup):
    # FIXME - I don't like it
    level = logging.WARNING
    if args.verbosity:
        level = logging.INFO
        setup.change_root_level(level)
        setup.change_stream_level(level)
    if args.log:
        setup.set_file_log(args.log, level)
        logging.getLogger(__name__).info("log file is {}".format(args.log))


def set_output_args(parser: ArgumentParser):
    group = parser.add_argument_group("output files")
    group.add_argument("-d", "--directory", metavar="dir",
                       default="OUTPUT",
                       help=messages["output-dir"])
    group.add_argument("-n", "--number-solutions", metavar="num",
                       default=3, type=int,
                       help=messages["number-of-solutions"])


def get_output_args(args) -> Tuple[str, int]:
    logger = logging.getLogger(__name__)
    directory = getattr(args, "directory")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    num_solutions = getattr(args, "number_solutions")
    if num_solutions < 1:
        logger.error("Number of solutions must be greater than one")
        exit(-1)
    logger.info("Output directory is {}".format(directory))
    logger.info("Number of solutions saved for each iteration is {}".format(
        num_solutions
    ))
    return directory, num_solutions
