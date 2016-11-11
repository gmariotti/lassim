from typing import List

from sortedcontainers import SortedList

from core.serializers.csv_serializer import CSVSerializer
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class SimpleCSVSolutionsHandler(SolutionsHandler):
    """
    A simple SolutionsHandler with just a CSV serializer.
    """

    def __init__(self, output_dir: str, num_solutions: int, headers: List[str]):
        self.csv_serializer = CSVSerializer.new_instance(
            output_dir, num_solutions, headers
        )

    def handle_solutions(self, solutions: SortedList, filename: str = None):
        self.csv_serializer.serialize_solutions(solutions, filename)
