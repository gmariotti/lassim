import os
from typing import List, Callable

from sortedcontainers import SortedList

from core.handlers.serializers.csv_serializer import CSVSerializer
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def default_filename_creator(num_solutions: int, num_variables: int) -> str:
    return "top{}solutions_{}variables_{}.csv".format(
        str(num_solutions), str(num_variables), str(os.getpid())
    )


def default_dirname_creator(num_solutions: int, num_variables: int) -> str:
    return "{}_vars_top{}".format(num_solutions, num_variables)


class SimpleCSVSolutionsHandler(SolutionsHandler):
    """
    Simple SolutionsHandler with just a CSV handler.
    """

    def __init__(self, output_dir: str, num_solutions: int, headers: List[str],
                 filename_creator: Callable[[int, int], str]
                 = default_filename_creator):
        self.csv_serializer = CSVSerializer.new_instance(
            output_dir, num_solutions, headers, filename_creator
        )

    def handle_solutions(self, solutions: SortedList, filename: str = None):
        self.csv_serializer.serialize_solutions(solutions, filename)


class DirectoryCSVSolutionsHandler(SolutionsHandler):
    """
    SolutionsHandler for serializing each solution as an independent file
    with the set inside a custom directory.
    """

    def __init__(self, output_dir: str, num_solutions: int, headers: List[str],
                 dirname_creator: Callable[[int, int], str] =
                 default_dirname_creator,
                 filename_creator: Callable[[int, int], str]
                 = None):
        self._serializer = CSVSerializer.new_instance(
            output_dir, 1, headers, filename_creator
        )
        self._dirname_creator = dirname_creator
        self._directory = output_dir
        self._num_solutions = num_solutions

    def handle_solutions(self, solutions: SortedList, dirname: str = None):
        num_to_print = min(len(solutions), self._num_solutions)
        if dirname is None:
            dirname = self._dirname_creator(
                solutions[0].number_of_variables, num_to_print
            )

        filename = "best{}.csv"
        directory = self._directory + "/" + dirname
        if not os.path.isdir(directory):
            os.makedirs(directory)
        for i in range(num_to_print):
            self._serializer.serialize_solutions(
                SortedList([solutions[i]]),
                dirname + "/" + filename.format(i + 1)
            )
