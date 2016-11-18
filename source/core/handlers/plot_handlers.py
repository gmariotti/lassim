import os
from typing import List, Tuple, Callable

from sortedcontainers import SortedList

from core.base_solution import BaseSolution
from core.handlers.serializers.plot_serializer import PlotSerializer
from core.solutions_handler import SolutionsHandler
from utilities.type_aliases import Tuple3V

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


def default_plotname_creator(directory: str, names: List[str],
                             solution: BaseSolution) -> str:
    pid = os.getpid()
    num_variables = solution.number_of_variables
    output_dir = "{}/{}".format(directory, num_variables)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    for name in names:
        yield "{}/{}_{}.png".format(output_dir, name, pid)


class PlotBestSolutionsHandler(SolutionsHandler):
    def __init__(self, directory: str, fig_names: List[str],
                 axis: List[Tuple[str, str]],
                 res_ode: Callable[[BaseSolution], Tuple3V],
                 name_creator: Callable[[str, List[str], BaseSolution], str]
                 = default_plotname_creator):
        self.plot_serializer = PlotSerializer.new_instance(
            directory, fig_names, axis, res_ode, name_creator
        )

    def handle_solutions(self, list_of_solutions: SortedList):
        best_solution = list_of_solutions[0]
        self.plot_serializer.serialize_solution(best_solution)
