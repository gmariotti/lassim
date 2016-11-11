import logging
import os
from typing import List, Callable

from sortedcontainers import SortedList

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


def default_filename_creator(num_solutions: int, num_variables: int) -> str:
    return "top{}solutions_{}variables.csv".format(
        str(num_solutions), str(num_variables)
    )


class CSVSerializer:
    """
    This class represents a serializer of solutions in a csv formatted file.
    """

    def __init__(self, directory: str, num_to_print: int, headers: List[str],
                 filename_creator: Callable[[int, int], str]):
        self._directory = directory
        self._num = num_to_print
        self._headers = headers
        self._filename_creator = filename_creator
        self._separator = "\t"

    @classmethod
    def new_instance(cls, output_dir: str, num_to_print: int,
                     headers: List[str],
                     filename_creator: Callable[[int, int], str]
                     = default_filename_creator) -> 'CSVSerializer':
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        if len(headers) == 0:
            raise RuntimeError(
                "List of headers for solutions serialization is empty."
            )
        return CSVSerializer(
            output_dir, num_to_print, headers, filename_creator
        )

    def serialize_solutions(self, solutions: SortedList, filename: str = None):
        if filename is None:
            filename = self._filename_creator(
                self._num, solutions[0].number_of_variables
            )
        num_solutions_to_print = min(len(solutions), self._num)
        with open(self._directory + "/" + filename, "w") as output:
            for i in range(0, num_solutions_to_print):
                solution = solutions[i]
                s_matrix = solution.get_solution_matrix(headers=self._headers)
                output.write(s_matrix.to_csv(sep=self._separator, index=False))
                output.write("Cost{}{}\n".format(
                    self._separator, solution.cost
                ))
        logging.getLogger(__name__).info(
            "Created file {} in directory {}".format(filename, self._directory)
        )
