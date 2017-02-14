import logging
import os
from typing import List, Callable

from sortedcontainers import SortedList

from core.base_solution import BaseSolution
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def serialize_solution(solution: BaseSolution, filename: str, directory: str,
                       headers: List[str], separator: str = "\t",
                       print_cost: bool = True, override: bool = True,
                       append: bool = True):
    """
    Serializes a solution into a csv file. The matrix to use is the one returned
    from an instance of BaseSolution.

    :param solution: BaseSolution to serialize.
    :param filename: Name of the file where to save the solution.
    :param directory: Name of the directory where to save the file.
    :param headers: Headers to use in the csv file.
    :param separator: Type of separator to use. Default is tab.
    :param print_cost: Boolean for printing or not a row with the cost of
        serialized solution. Default is True.
    :param override: Boolean for override the file if it exist or not.
        Default is True.
    :param append: Boolean for append the current solution to the end of the
        file if it exist. Default is True.
    :raise RuntimeWarning: If the file exist and override is set to False.
    """

    path = directory + "/" + filename
    if not override and os.path.isfile(path):
        raise RuntimeWarning("File {} already exist.".format(path))
    option = "w"
    if append:
        option = "a"
    with open(path, option) as output:
        sol_matrix = solution.get_solution_matrix(headers)
        output.write(sol_matrix.to_csv(sep=separator, index=False))
        if print_cost:
            output.write("Cost{}{}\n".format(separator, solution.cost))


def default_filename_creator(solutions: SortedList, num_solutions: int) -> str:
    num_variables = solutions[0].number_of_variables
    return "top{}solutions_{}variables_{}.csv".format(
        str(num_solutions), str(num_variables), str(os.getpid())
    )


def default_dirname_creator(solutions: SortedList, num_solutions: int) -> str:
    num_variables = solutions[0].number_of_variables
    return "{}_vars_top{}".format(num_variables, num_solutions)


class SimpleCSVSolutionsHandler(SolutionsHandler):
    """
    Simple SolutionsHandler that serializes the solutions inside a CSV file.
    """

    def __init__(self, output_dir: str, num_solutions: int, headers: List[str],
                 filename_creator: Callable[[SortedList, int], str]
                 = default_filename_creator):
        """
        Constructor of a SimpleCSVSolutionsHandler.

        :param output_dir: The output directory where to save the solutions. It
            is created if it doesn't exist.
        :param num_solutions: Number of solutions to save for each list of
            solutions.
        :param headers: Headers to use for each solution.
        :param filename_creator: Function for creating a filename by using as
            input the list of solutions and the number of solutions to print.
        :raise RuntimeError: If the list containing the headers is empty.
        """

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        self._output_dir = output_dir
        self._num_solutions = num_solutions
        if len(headers) == 0:
            raise RuntimeError(
                "List of headers for solutions serialization is empty"
            )
        self._headers = headers
        self._name_creator = filename_creator

    def handle_solutions(self, solutions: SortedList, filename: str = None):
        to_save = min(len(solutions), self._num_solutions)
        if filename is None:
            filename = self._name_creator(solutions, to_save)
        for i in range(to_save):
            serialize_solution(
                solutions[i], filename, self._output_dir, self._headers
            )
        logging.getLogger(__name__).info(
            "Created file {} in directory {}".format(filename, self._output_dir)
        )


class DirectoryCSVSolutionsHandler(SolutionsHandler):
    """
    SolutionsHandler for serializing each solution as an independent file
    with the set inside a custom directory.
    """

    def __init__(self, output_dir: str, num_solutions: int, headers: List[str],
                 dirname_creator: Callable[[SortedList, int], str] =
                 default_dirname_creator,
                 filename_creator: Callable[[SortedList, int], str] =
                 default_filename_creator):
        """
        Object for saving a list of solutions as independent CSV files in their
        own directory. The directory can be generated thanks to a name creator
        function or passed as input.

        :param output_dir: The name of the main directory where the generated
            folders will go.
        :param num_solutions: Number of solutions to print for each list.
        :param headers: Headers for the CSV file.
        :param dirname_creator: Function that given as input the number of
            variables of a solution and the number of solutions to print, it
            generates a valid directory name.
        """
        self._handler = SimpleCSVSolutionsHandler(
            output_dir, 1, headers, filename_creator
        )
        self._dirname_creator = dirname_creator
        self._directory = output_dir
        self._num_solutions = num_solutions

    def handle_solutions(self, solutions: SortedList, dirname: str = None,
                         name_creator: Callable[[int], str] =
                         lambda i: "best_{}.csv".format(i)):
        num_to_print = min(len(solutions), self._num_solutions)
        if dirname is None:
            dirname = self._dirname_creator(solutions, num_to_print)

        directory = self._directory + "/" + dirname
        if not os.path.isdir(directory):
            os.makedirs(directory)

        for i in range(num_to_print):
            self._handler.handle_solutions(
                SortedList(solutions[i:i + 1]),
                dirname + "/" + name_creator(i + 1)
            )
