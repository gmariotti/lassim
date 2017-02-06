import json
import logging
import os
from argparse import ArgumentParser
from typing import Dict, Tuple, List

import psutil

from core.factories import OptimizationFactory
from core.lassim_context import OptimizationArgs
from utilities.configuration import ConfigurationParser, ConfigurationBuilder
from utilities.data_classes import InputFiles, OutputData
from utilities.logger_setup import LoggerSetup
from utilities.terminal import set_logger_args

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def output_conversion(output_dict: Dict):
    logger = logging.getLogger(__name__)
    directory = output_dict["directory"]
    if directory is not None and not os.path.isdir(directory):
        os.makedirs(directory)
        logger.info("Created output directory {}".format(directory))

    num_solutions = 1
    if output_dict["num solutions"] is not None:
        num_solutions = int(output_dict["num solutions"])
        if num_solutions < 1:
            logger.error("Number of solutions must be greater than one.")
            num_solutions = 1

    logger.info("Number of solutions saved for each iteration is {}".format(
        num_solutions
    ))

    return {
        "directory": directory,
        "num_solutions": int(output_dict["num solutions"])
    }


def optimization_conversion(optimization_dict: Dict):
    logger = logging.getLogger(__name__)
    algorithm = OptimizationFactory.cus_default()
    if optimization_dict["type"] is not None:
        algorithm = optimization_dict["type"].upper()

    params = {}
    if optimization_dict["parameters"] is not None:
        with open(optimization_dict["parameters"]) as params_json:
            params = json.load(params_json)

    cores = psutil.cpu_count()
    if optimization_dict["cores"] is not None:
        cores = int(optimization_dict["cores"])
        if cores < 1:
            raise RuntimeError

    evolvs = 1
    if optimization_dict["evolutions"] is not None:
        evolvs = int(optimization_dict["evolutions"])
        if evolvs < 1:
            raise RuntimeError

    individuals = 1
    if optimization_dict["individuals"] is not None:
        individuals = int(optimization_dict["individuals"])
        if individuals < 1:
            raise RuntimeError

    pert_factor = 0
    if optimization_dict["perturbation factor"] is not None:
        pert_factor = float(optimization_dict["perturbation factor"])
        if pert_factor < 0 or pert_factor > 1:
            raise RuntimeError

    return {
        "opt_type": algorithm, "params": params, "num_cores": cores,
        "evolutions": evolvs, "individuals": individuals,
        "pert_factor": pert_factor
    }


def core_terminal(script_name: str
                  ) -> Tuple[InputFiles, OutputData,
                             List[OptimizationArgs], List[OptimizationArgs]]:
    logger = logging.getLogger(__name__)
    # parse terminal option
    parser = ArgumentParser(script_name)
    parser.add_argument("configuration", metavar="file.ini",
                        help="Some message about configuration")
    parser.add_argument("-c", "--configuration-helper", action="store_true",
                        help="TODO")
    set_logger_args(parser)
    args = parser.parse_args()
    if getattr(args, "configuration_helper"):
        core_configuration_example(args.configuration)
        exit(0)

    config = ConfigurationParser(args.configuration).define_section(
        "Input Data", "network", "data", "times", "perturbations"
    ).define_section(
        "Optimization", "type", "parameters", "cores", "evolutions",
        "individuals", "perturbation factor"
    ).define_section(
        "Output", "directory", "num solutions"
    ).define_section(
        "Logging", "log", "verbosity"
    )

    config.parse_logger_section("Logging", LoggerSetup())

    files = config.parse_section("Input Data", InputFiles, input_validity_check)
    is_pert = False
    if files.perturbations is not None:
        is_pert = True

    output = config.parse_section("Output", OutputData, output_conversion)

    main_opt = config.parse_section(
        "Optimization", OptimizationArgs, optimization_conversion
    )
    logger.info("Logging Core Optimization arguments...")
    main_opt.log_args(logger, is_pert)

    return files, output, [main_opt], list()


def core_configuration_example(ini_file: str):
    ConfigurationBuilder(ini_file).add_section(
        "Input Data", "Section containing the data for the toolbox"
    ).add_key_value(
        "network", "file", "File representing the network"
    ).add_key_values(
        "data", ["file1", "file2"], "2 or more data time files"
    ).add_key_value(
        "times", "file", "Time instance file compatible with previous data"
    ).add_optional_key_value(
        "perturbations", "file", "Value for the perturbations file."
    ).add_section(
        "Optimization", "Section containing the optimization parameters"
    ).add_optional_key_value(
        "type", OptimizationFactory.cus_default(),
        "Optimization algorithm to use",
        "List of possible arguments is {}".format(
            ", ".join(OptimizationFactory.labels_cus())
        ), "http://esa.github.io/pygmo/documentation/algorithms.html for info"
    ).add_optional_key_value(
        "parameters", "file.json", "Optimization parameters"
    ).add_optional_key_value(
        "cores", str(psutil.cpu_count()),
        "Number of cores to use for optimization"
    ).add_optional_key_value(
        "evolutions", "1", "Number of evolutions to run"
    ).add_optional_key_value(
        "individuals", "1", "Number of individuals per island"
    ).add_optional_key_value(
        "perturbation factor", "0",
        "Weight of perturbations in cost function", "Must be between 0 and 1"
    ).add_section(
        "Output", "Section containing info for the output of the toolbox"
    ).add_optional_key_value(
        "directory", "dir", "Directory where to put the solutions"
    ).add_optional_key_value(
        "num solutions", "1", "Number of solutions to save for each iteration"
    ).add_section(
        "Logging", "Section containing options for toolbox logging"
    ).add_optional_key_value(
        "log", "file", "Name of the file where to save the logging information"
    ).add_optional_key_value(
        "verbosity", "False",
        "Set to True in order to increase verbosity of the toolbox"
    ).build()

    print("Generated {} as example.".format(ini_file))


def input_validity_check(files: Dict) -> Dict:
    logger = logging.getLogger(__name__)

    check_file_validity(files["network"], logger)
    if len(files["data"]) < 2:
        logger.error("Expected two or more input files for data.")
        raise RuntimeError("See log for more information.")
    for data_file in files["data"]:
        check_file_validity(data_file, logger)
    check_file_validity(files["times"], logger)

    logger.info("Network file is {}".format(files["network"]))
    logger.info("Data file are {}".format(", ".join(files["data"])))
    logger.info("Time series file is {}".format(files["times"]))

    if files["perturbations"] is not None:
        check_file_validity(files["perturbations"], logger)
        logger.info("Perturbations file is {}".format(files["perturbations"]))

    return files


def check_file_validity(filename: str, logger: logging.Logger):
    if not os.path.isfile(filename):
        logger.error("File {} doesn't exist.".format(filename))
        raise RuntimeError("See log for more information.")