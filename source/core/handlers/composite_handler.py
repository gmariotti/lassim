from typing import List

from sortedcontainers import SortedList

from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class CompositeSolutionsHandler(SolutionsHandler):
    """
    A SolutionsHandler that accepts one or more SolutionsHandler and dispatch
    to the the list of solutions
    """

    def __init__(self, handlers_list: List[SolutionsHandler]):
        self._handlers = handlers_list

    def handle_solutions(self, list_of_solutions: SortedList):
        for handler in self._handlers:
            handler.handle_solutions(list_of_solutions)
