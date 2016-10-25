from sortedcontainers import SortedList

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class SolutionsHandler:
    """
    Functional Interface for implementing an Handler.
    Every implementation should just take care on how to handle a SortedList of
    solutions received as parameter.
    """

    def handle_solutions(self, list_of_solutions: SortedList):
        raise NotImplementedError(self.handle_solutions.__name__)
