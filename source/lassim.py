import logging

import numpy as np

from core.serializers.csv_serializer import CSVSerializer
from customs.core_creation import optimization_setup, optimization_run
from utilities.logger_setup import LoggerSetup
from utilities.terminal import parse_terminal

"""
Example script of the lassim toolbox.
After the setup of the logger and the parsing of the arguments from terminal,
an optimization object is created in order to perform the core optimization.

This script and the functions used in it are a typical example of how the
toolbox works.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


def lassim():
    setup = LoggerSetup()
    files, output, opt_args = parse_terminal("lassim", setup)
    serializer = CSVSerializer.new_instance(output[0], output[1])
    optimization, handler = optimization_setup(
        files, opt_args, serializer,
    )

    try:
        optimization_run(
            optimization, opt_args.num_islands, opt_args.individuals, handler
        )
    except Exception:
        logging.exception("Exception occurred during optimization")


if __name__ == "__main__":
    # FIXME - for now, ignore all overflow problems. The only situation in which
    # this occurs is with exp - doesn't work
    # np.seterr(over="ignore")

    lassim()
