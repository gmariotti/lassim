import logging
import os
from typing import List, Callable

from sortedcontainers import SortedList

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


def default_filename_creator(num_solutions: int, num_variables: int) -> str:
    return "top{}solutions_{}variables.csv".format(
        str(num_solutions), str(num_variables)
    )


class CSVSerializer:
    """
    This class represents a serializer of solutions in a csv formatted file.
    """

    def __init__(self, directory: str, num_to_print: int,
                 filename_creator: Callable[[int, int], str], headers: str):
        self._directory = directory
        self._num = num_to_print
        self._filename_creator = filename_creator
        self._headers = headers
        self._separator = "\t"

    @classmethod
    def new_instance(cls, output_dir: str, num_to_print: int,
                     filename_creator: Callable[[int, int], str]
                     = default_filename_creator,
                     headers: List[str] = None) -> 'CSVSerializer':
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        headers_line = None if headers is None else "\t".join(headers)
        return CSVSerializer(
            output_dir, num_to_print, filename_creator, headers_line
        )

    def set_headers(self, headers: List[str]):
        self._headers = self._separator.join(headers)

    def serialize_solutions(self, solutions: SortedList, filename: str = None):
        if filename is None:
            filename = self._filename_creator(
                self._num, solutions[0].get_number_of_variables()
            )
        num_solutions_to_print = min(len(solutions), self._num)
        with open(self._directory + "/" + filename, "w") as output:
            for i in range(0, num_solutions_to_print):
                if self._headers is not None:
                    output.write(self._headers + "\n")
                solution = solutions[i]
                sol_matrix = solution.get_solution_matrix()
                for line in sol_matrix:
                    output.write(
                        self._separator.join(str(val) for val in line) + "\n"
                    )
                output.write("Cost{}{}\n".format(
                    self._separator, solution.get_cost()
                ))
        logging.getLogger(__name__).info(
            "Created file {} in directory {}".format(filename, self._directory)
        )
