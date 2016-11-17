import json
import logging
import os
from argparse import ArgumentParser
from typing import Dict, Tuple

import psutil

from core.factories import OptimizationFactory
from core.lassim_context import OptimizationArgs
from utilities.logger_setup import LoggerSetup

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"

messages = {
    # MANDATORY
    "input-network": "The file path of the transcription factors network.",
    "input-data": "The files path of the data to analyze. "
                  "Expected at least two files",
    "time-series": "The file path of the time series in which the data where "
                   "collected.",
    "input-pert": "The file path of the perturbations file.",

    # OPTIONAL
    # CORE OPTIONS
    "c-opt-type": "Type of optimization algorithm to use for the Core. "
                  "http://esa.github.io/pygmo/documentation/algorithms.html "
                  "for the parameters. Valid one are {}.",
    "c-opt-json": "JSON file with the parameters for optimization of the Core.",
    "c-cores": "Number of cores used for optimization of the Core. Default for "
               "this system is {}.",
    "c-evolutions": "Number of evolutions for each archipelago for the Core. "
                    "Default is {}.",
    "c-individuals": "Number of individuals used in the optimization algorithm "
                     "of the Core. Default is {}.",
    "c-pert-factor": "Indicates the importance of the perturbations in the "
                     "objective function of the Core. Must be a value between 0"
                     " and 1. Default is {}.",

    # GENERAL
    "log": "Sets the name of the file where to save the logs other than on "
           "screen.",
    "verbosity": "Increase verbosity of logs from WARNING to INFO.",
    "output-dir": "Name of directory for output files.",
    "number-of-solutions": "For each iteration, number of solutions to save."
}

default = {
    "cores": psutil.cpu_count(),
    "evolutions": 1,
    "individuals": 6,
    "pert-factor": 0
}


def set_terminal_args(name: str) -> ArgumentParser:
    parser = ArgumentParser(name)
    # set terminal options
    set_files_args(parser)
    set_core_optimization_args(parser)
    set_logger_args(parser)
    set_output_args(parser)

    return parser


def set_files_args(parser: ArgumentParser):
    group = parser.add_argument_group("input data")
    group.add_argument("inputN", metavar="input-network",
                       help=messages["input-network"])
    # group.add_argument("inputD", metavar="input-data",
    #                    help=messages["input-data"])
    group.add_argument("inputD", metavar="input-data", nargs="+",
                       help=messages["input-data"])
    group.add_argument("inputT", metavar="time-series",
                       help=messages["time-series"])
    group.add_argument("--perturbations", metavar="input-perturbations",
                       help=messages["input-pert"])


def set_core_optimization_args(parser: ArgumentParser):
    group = parser.add_argument_group("core optimization")
    group.add_argument("-cO", "--cOptimization", metavar="type",
                       choices=OptimizationFactory.labels_cus(),
                       default=OptimizationFactory.cus_default(),
                       help=messages["c-opt-type"].format(
                           ", ".join(OptimizationFactory.labels_cus())
                       ))
    group.add_argument("-cP", "--cParameters", metavar="json",
                       help=messages["c-opt-json"])
    group.add_argument("-cC", "--cCores", metavar="num",
                       default=default["cores"], type=int,
                       help=messages["c-cores"].format(default["cores"]))
    group.add_argument("-cE", "--cEvolutions", metavar="num",
                       default=default["evolutions"], type=int,
                       help=messages["c-evolutions"].format(
                           default["evolutions"]
                       ))
    group.add_argument("-cI", "--cIndividuals", metavar="num",
                       default=default["individuals"], type=int,
                       help=messages["c-individuals"].format(
                           default["individuals"]
                       ))
    group.add_argument("--cPerturbations-factor", metavar="num",
                       default=default["pert-factor"], type=float,
                       help=messages["c-pert-factor"].format(
                           default["pert-factor"]
                       ))


def set_logger_args(parser: ArgumentParser):
    group = parser.add_argument_group("log options")
    group.add_argument("-l", "--log", metavar="file",
                       help=messages["log"])
    group.add_argument("-v", "--verbosity", action="store_true",
                       help=messages["verbosity"])


def set_output_args(parser: ArgumentParser):
    group = parser.add_argument_group("output files")
    group.add_argument("-d", "--directory", metavar="dir",
                       default="OUTPUT",
                       help=messages["output-dir"])
    group.add_argument("-n", "--number-solutions", metavar="num",
                       default=3, type=int,
                       help=messages["number-of-solutions"])


def get_terminal_args(parser: ArgumentParser
                      ) -> (Dict[str, str], Tuple[str, int], OptimizationArgs):
    setup = LoggerSetup()

    # retrieve input from terminal
    args = parser.parse_args()
    get_logger_args(args, setup)
    files, is_pert = get_files_args(args)
    output = get_output_args(args)
    core_args = get_core_optimization_args(args)
    core_args.log_args(logging.getLogger(__name__), is_pert)

    return files, output, core_args


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


def get_files_args(args) -> (Dict[str, str], bool):
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


def get_core_optimization_args(args) -> OptimizationArgs:
    algorithm = args.cOptimization
    params = {}
    param_filename = args.cParameters
    if param_filename is not None and os.path.isfile(param_filename):
        with open(param_filename) as params_json:
            params = json.load(params_json)

    # get cores - checks if the user puts 0 or less. In this case uses the
    # default number in this system
    cores = args.cCores
    if cores <= 0:
        cores = default["cores"]

    evols = args.cEvolutions
    if evols <= 0:
        evols = default["evolutions"]

    individuals = args.cIndividuals
    if individuals <= 0:
        individuals = default["individuals"]

    pert_factor = getattr(args, "cPerturbations_factor")
    if pert_factor < 0 or pert_factor > 1:
        pert_factor = default["pert-factor"]

    return OptimizationArgs(
        algorithm, params, cores, evols, individuals, pert_factor
    )


def get_output_args(args) -> (str, int):
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
