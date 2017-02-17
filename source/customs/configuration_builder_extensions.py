import psutil

from core.factories import OptimizationFactory
from utilities.configuration import ConfigurationBuilder

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

"""
Extension methods for the ConfigurationBuilder, used in order to avoid
overloading of the class with specific methods.
Use 'import custom.configuration_extensions' in the function that wants to
use them.
"""


def optimization_section(config: ConfigurationBuilder) -> ConfigurationBuilder:
    return config.add_section(
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
    )


ConfigurationBuilder.add_optimization_section = optimization_section


def output_section(config: ConfigurationBuilder) -> ConfigurationBuilder:
    return config.add_section(
        "Output", "Section containing info for the output of the toolbox"
    ).add_optional_key_value(
        "directory", "dir", "Directory where to put the solutions"
    ).add_optional_key_value(
        "num solutions", "1", "Number of solutions to save for each iteration"
    ).add_optional_key_value(
        "best result", "file",
        "Name of the file where to save the best optimization solution"
    )


ConfigurationBuilder.add_output_section = output_section


def logger_section(config: ConfigurationBuilder) -> ConfigurationBuilder:
    return config.add_section(
        "Logging", "Section containing options for toolbox logging"
    ).add_optional_key_value(
        "log", "file", "Name of the file where to save the logging information"
    ).add_optional_key_value(
        "verbosity", "True",
        "Set to True in order to increase verbosity of the toolbox"
    )


ConfigurationBuilder.add_logger_section = logger_section
