from utilities.configuration import ConfigurationParser

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def optimization_section(config: ConfigurationParser):
    return config.define_section(
        "Optimization", "type", "parameters", "cores", "evolutions",
        "individuals", "perturbation factor"
    )


ConfigurationParser.define_optimization_section = optimization_section


def output_section(config: ConfigurationParser):
    return config.define_section(
        "Output", "directory", "num solutions", "best result"
    )


ConfigurationParser.define_output_section = output_section


def logger_section(config: ConfigurationParser):
    return config.define_section(
        "Logging", "log", "verbosity"
    )


ConfigurationParser.define_logger_section = logger_section
