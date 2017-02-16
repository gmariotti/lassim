import json
import logging
import os
from argparse import ArgumentParser
from typing import Dict, Tuple, List, Callable

import psutil

from core.factories import OptimizationFactory
from core.lassim_context import OptimizationArgs
from utilities.configuration import ConfigurationParser, ConfigurationBuilder
from utilities.data_classes import InputFiles, OutputFiles, CoreFiles, \
    InputExtra
from utilities.logger_setup import LoggerSetup

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


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
            raise RuntimeError("Expected at least 1 core!")

    evolvs = 1
    if optimization_dict["evolutions"] is not None:
        evolvs = int(optimization_dict["evolutions"])
        if evolvs < 1:
            raise RuntimeError("Expected at least 1 evolution!")

    individuals = 1
    if optimization_dict["individuals"] is not None:
        individuals = int(optimization_dict["individuals"])
        if individuals < 1:
            raise RuntimeError("Expected at least 1 individual!")

    pert_factor = 0
    if optimization_dict["perturbation factor"] is not None:
        pert_factor = float(optimization_dict["perturbation factor"])
        if pert_factor < 0 or pert_factor > 1:
            raise RuntimeError("perturbation factor must be between 0 and 1!")

    return {
        "opt_type": algorithm, "params": params, "num_cores": cores,
        "evolutions": evolvs, "individuals": individuals,
        "pert_factor": pert_factor
    }


def extra_conversion(extra_input: Dict):
    num_tasks = int(extra_input["num tasks"])
    if num_tasks < 1:
        raise RuntimeError("number of tasks must be >= 1")
    return {
        "num_tasks": num_tasks
    }


def core_input_check(files: Dict):
    logger = logging.getLogger(__name__)
    check_file_validity(files["core system"], logger)
    check_file_validity(files["perturbations"], logger)
    check_file_validity(files["y0"], logger)

    logger.info("Core System file is {}".format(files["core system"]))
    logger.info("Core Perturbations file is {}".format(files["perturbations"]))
    logger.info("Core y0 file is {}".format(files["y0"]))

    return {
        "core_system": files["core system"],
        "core_pert": files["perturbations"],
        "core_y0": files["y0"]
    }


# noinspection PyUnresolvedReferences
def parse_core_config(args) -> Tuple[InputFiles, OutputFiles,
                                     List[OptimizationArgs],
                                     List[OptimizationArgs]]:
    import customs.configuration_parser_extensions

    logger = logging.getLogger(__name__)

    config = ConfigurationParser(args.configuration).define_section(
        "Input Data", "network", "data", "times", "perturbations"
    ).define_optimization_section().define_output_section(
    ).define_logger_section()

    config.parse_logger_section("Logging", LoggerSetup())

    files = config.parse_section("Input Data", InputFiles, input_validity_check)
    is_pert = False
    if files.perturbations is not None:
        is_pert = True

    output = config.parse_section("Output", OutputFiles, output_conversion)

    main_opt = config.parse_section(
        "Optimization", OptimizationArgs, optimization_conversion
    )
    logger.info("Logging Core Optimization arguments...")
    main_opt.log_args(logger, is_pert)

    return files, output, [main_opt], list()


# noinspection PyUnresolvedReferences
def core_configuration_example(ini_file: str):
    import customs.configuration_builder_extensions

    ConfigurationBuilder(ini_file).add_section(
        "Input Data", "Section containing the data for the toolbox"
    ).add_key_value(
        "network", "file", "File representing the network"
    ).add_key_values(
        "data", ["file1", "file2", ".."], "2 or more data time files"
    ).add_key_value(
        "times", "file", "Time instance file compatible with previous data"
    ).add_optional_key_value(
        "perturbations", "file", "Value for the perturbations file"
    ).add_optimization_section().add_output_section(
    ).add_logger_section().build()

    print("Generated {} as example.".format(ini_file))


# noinspection PyUnresolvedReferences
def parse_peripherals_config(args) -> Tuple[ConfigurationParser, InputFiles,
                                            CoreFiles, OutputFiles,
                                            List[OptimizationArgs],
                                            List[OptimizationArgs], InputExtra]:
    import customs.configuration_parser_extensions

    logger = logging.getLogger(__name__)

    config = ConfigurationParser(args.configuration).define_section(
        "Input Data", "network", "data", "times", "perturbations"
    ).define_section(
        "Core Files", "core system", "perturbations", "y0"
    ).define_section(
        "Extra", "num tasks"
    ).define_optimization_section().define_output_section(
    ).define_logger_section()

    config.parse_logger_section("Logging", LoggerSetup)

    files = config.parse_section("Input Data", InputFiles, input_validity_check)
    core_files = config.parse_section(
        "Core Files", CoreFiles, core_input_check
    )
    is_pert = False
    if files.perturbations is not None and core_files.perturbations is not None:
        is_pert = True

    extra = config.parse_section("Extra", InputExtra, extra_conversion)
    output = config.parse_section("Output", OutputFiles, output_conversion)

    main_opt = config.parse_section(
        "Optimization", OptimizationArgs, optimization_conversion
    )
    logger.info("Logging Core Optimization arguments...")
    main_opt.log_args(logger, is_pert)

    return config, files, core_files, output, [main_opt], list(), extra


def default_terminal(name: str, helper: Callable[[str], None]):
    parser = ArgumentParser(name)
    parser.add_argument("configuration", metavar="file.ini",
                        help="Some message about configuration")
    parser.add_argument("-c", "--configuration-helper", action="store_true",
                        help="TODO")
    args = parser.parse_args()
    if getattr(args, "configuration_helper"):
        helper(args.configuration)
        exit(0)
    return args


# noinspection PyUnresolvedReferences
def peripheral_configuration_example(ini_file: str):
    import customs.configuration_builder_extensions

    ConfigurationBuilder(ini_file).add_section(
        "Input Data", "Section containing the data for the toolbox"
    ).add_key_value(
        "network", "file",
        "File containing the network file with the list of peripheral genes"
    ).add_key_values(
        "data", ["file1", "file2"], "2 or more data time files"
    ).add_key_value(
        "times", "file", "Time instance file compatible with previous data"
    ).add_optional_key_value(
        "perturbations", "file", "Value for the peripherals' perturbations file"
    ).add_section(
        "Core Files", "Section containing the data of a completed core"
    ).add_key_value(
        "core system", "file", "File containing the parameters of the core"
    ).add_optional_key_value(
        "perturbations", "file", "Value for the perturbations file of the core"
    ).add_key_value(
        "y0", "file",
        "File containing the starting point for each transcription factor"
    ).add_section(
        "Extra", "Extra parameters to use"
    ).add_key_value(
        "num tasks", "1", "Number of parallel tasks to run"
    ).add_optimization_section().add_output_section(
    ).add_logger_section().build()

    print("Generated configuration file example {}".format(ini_file))


def check_file_validity(filename: str, logger: logging.Logger):
    if not os.path.isfile(filename):
        logger.error("File {} doesn't exist.".format(filename))
        raise RuntimeError("See log for more information.")
