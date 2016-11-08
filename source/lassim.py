import logging

from core.serializers.csv_serializer import CSVSerializer
from customs.core_creation import optimization_setup, optimization_run
from utilities.terminal import get_terminal_args, set_terminal_args

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
    script_name = "lassim"
    files, output, opt_args = get_terminal_args(set_terminal_args(script_name))
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
    lassim()
