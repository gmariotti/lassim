from sortedcontainers import SortedList

from core.serializers.csv_serializer import CSVSerializer
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class SimpleCSVSolutionsHandler(SolutionsHandler):
    """
    A simple SolutionsHandler with just a CSV serializer.
    """

    def __init__(self, serializer: CSVSerializer):
        self.csv_serializer = serializer

    def handle_solutions(self, solutions: SortedList, filename: str = None):
        self.csv_serializer.serialize_solutions(solutions, filename)
