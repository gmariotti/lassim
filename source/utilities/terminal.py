import json
import logging
import os
from argparse import ArgumentParser
from typing import Dict, Tuple

import psutil

from core.base_optimization import OptimizationArgs
from core.factories import OptimizationFactory
from utilities.logger_setup import LoggerSetup

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

messages = {
    # MANDATORY
    "input-network": "The file path of the transcription factors network.",
    "input-data": "The file path of the data to analyze.",
    "time-series": "The file path of the time series in which the data where "
                   "collected.",
    "input-sigma": "The file path of the sigma for evaluation - TODO remove",
    "input-pert": "The file path of the perturbations file.",

    # OPTIONAL
    "optimization-type": "Type of optimization algorithm to use. "
                         "DE = Differential Evolution. "
                         "Default value is DE",
    "optimization-json": "JSON file with the parameters for optimization.",
    "cores": "Number of cores used for optimization. Default for this system"
             " is {}.",
    "evolutions": "Number of evolutions for each archipelago.",
    "log": "Sets the name of the file where to save the logs other than on "
           "screen.",
    "verbosity": "Increase verbosity of logs from WARNING to INFO.",
    "output-dir": "Name of directory for output files.",
    "number-of-solutions": "For each iteration, number of solutions to save."
}


def parse_terminal(setup: LoggerSetup
                   ) -> (Dict[str, str], Tuple[str, int], OptimizationArgs):
    parser = ArgumentParser(__name__)

    # set terminal options
    set_files_args(parser)
    set_optimization_args(parser)
    set_logger_args(parser)
    set_output_args(parser)

    # retrieve input from terminal
    args = parser.parse_args()
    get_logger_args(args, setup)
    files = get_files_args(args)
    output = get_output_args(args)
    optimization_args = get_optimization_args(args)

    return files, output, optimization_args


def set_files_args(parser: ArgumentParser):
    group = parser.add_argument_group("input data")
    group.add_argument("inputN", metavar="input-network",
                       help=messages["input-network"])
    group.add_argument("inputD", metavar="input-data",
                       help=messages["input-data"])
    group.add_argument("inputT", metavar="time-series",
                       help=messages["time-series"])
    # TODO - to be deleted
    group.add_argument("inputS", metavar="input-sigma",
                       help=messages["input-sigma"])
    group.add_argument("--perturbations", metavar="input-perturbations",
                       help=messages["input-pert"])


def set_optimization_args(parser: ArgumentParser):
    group = parser.add_argument_group("optimization")
    group.add_argument("-o", "--optimization",
                       choices=["DE"], default="DE",
                       help=messages["optimization-type"])
    group.add_argument("-p", "--parameters", metavar="json",
                       help=messages["optimization-json"])
    default_cores = psutil.cpu_count()
    group.add_argument("-c", "--cores", metavar="num",
                       default=default_cores, type=int,
                       help=messages["cores"].format(default_cores))
    group.add_argument("-e", "--evolutions", metavar="num",
                       default=1, type=int,
                       help=messages["evolutions"])


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


def get_logger_args(args, setup: LoggerSetup):
    # TODO - I don't like it
    level = logging.WARNING
    if args.verbosity:
        level = logging.INFO
        setup.change_root_level(level)
        setup.change_stream_level(level)
    if args.log:
        setup.set_file_log(args.log, level)
        logging.getLogger(__name__).info("log file is {}".format(args.log))


def get_files_args(args) -> Dict[str, str]:
    logger = logging.getLogger(__name__)
    if not os.path.isfile(args.inputN):
        logger.error("File {} doesn't exist".format(args.inputN))
        exit(0)
    if not os.path.isfile(args.inputD):
        logger.error("File {} doesn't exist".format(args.inputD))
        exit(0)
    if not os.path.isfile(args.inputT):
        logger.error("File {} doesn't exist".format(args.inputT))
        exit(0)
    if not os.path.isfile(args.inputS):
        logger.error("File {} doesn't exist".format(args.inputS))
        exit(0)

    files = {
        "network": args.inputN,
        "data": args.inputD,
        "time": args.inputT,
        "sigma": args.inputS,
    }
    pert_file = getattr(args, "perturbations")
    if pert_file is not None and not os.path.isfile(pert_file):
        logger.error("File {} doesn't exist.".format(pert_file))
        exit(0)
    logger.info("Network file is {}".format(args.inputN))
    logger.info("Data file is {}".format(args.inputD))
    logger.info("Time series file is {}".format(args.inputT))
    logger.info("Sigma file is {}".format(args.inputS))
    if pert_file is not None:
        logger.info("Perturbations file is {}".format(pert_file))
        files["perturbations"] = pert_file

    return files


def get_optimization_args(args) -> (str, Dict):
    algorithm = OptimizationFactory.get_optimization_type(args.optimization)
    params = {}
    param_filename = args.parameters
    if param_filename is not None and os.path.isfile(param_filename):
        with open(param_filename) as params_json:
            params = json.load(params_json)
    logger = logging.getLogger(__name__)
    logger.info("Algorithm used is {}".format(algorithm))

    # get cores - checks if the user puts 0 or less. In this case uses the
    # default number in this system
    cores = args.cores
    if cores <= 0:
        cores = psutil.cpu_count()
    logger.info("Number of cores is {}".format(cores))

    evols = args.evolutions
    if args.evolutions <= 0:
        evols = 1
    logger.info("Number of evolutions for archipelago is {}".format(evols))

    return OptimizationArgs(algorithm, params, cores, evols)


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
