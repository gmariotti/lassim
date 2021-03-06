import os
from typing import List, Callable

from sortedcontainers import SortedList

from core.handlers.serializers.csv_serializer import CSVSerializer
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


def default_filename_creator(num_solutions: int, num_variables: int) -> str:
    return "top{}solutions_{}variables_{}.csv".format(
        str(num_solutions), str(num_variables), str(os.getpid())
    )


class SimpleCSVSolutionsHandler(SolutionsHandler):
    """
    A simple SolutionsHandler with just a CSV serializer.
    """

    def __init__(self, output_dir: str, num_solutions: int, headers: List[str],
                 filename_creator: Callable[[int, int], str]
                 = default_filename_creator):
        self.csv_serializer = CSVSerializer.new_instance(
            output_dir, num_solutions, headers, filename_creator
        )

    def handle_solutions(self, solutions: SortedList, filename: str = None):
        self.csv_serializer.serialize_solutions(solutions, filename)
