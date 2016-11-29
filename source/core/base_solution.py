from copy import deepcopy
from typing import List

import numpy as np
import pandas as pd
from PyGMO.core import champion
from sortedcontainers import SortedDict

from core.lassim_problem import LassimProblem
from core.utilities.type_aliases import Float, Vector


class BaseSolution:
    def __init__(self, champ: champion, react_ids: SortedDict,
                 prob: LassimProblem):
        self.result = champ
        self._problem = prob
        self._solution = champ.x
        self._cost = champ.f[0]
        self._reactions_ids = react_ids

    @property
    def cost(self) -> float: return float(self._cost)

    @property
    def solution_vector(self) -> Vector:
        return np.array(self._solution, dtype=Float)

    @property
    def number_of_variables(self) -> int: return len(self._solution)

    @property
    def reactions_ids(self) -> SortedDict: return deepcopy(self._reactions_ids)

    def get_solution_matrix(self, headers: List[str]) -> pd.DataFrame:
        """
        Get a pandas.DataFrame representation of the solution. Must be
        implemented based on the kind of problem this solution wants to
        represent.
        :param: The list of headers for the pandas.DataFrame
        :return: A pandas.DataFrame representing the solution.
        """
        raise NotImplementedError(self.get_solution_matrix.__name__)

    def __ge__(self, other: 'BaseSolution'): return self.cost >= other.cost

    def __le__(self, other: 'BaseSolution'): return self.cost <= other.cost

    def __eq__(self, other: 'BaseSolution'): return self.cost == other.cost

    def __gt__(self, other: 'BaseSolution'): return self.cost > other.cost

    def __lt__(self, other: 'BaseSolution'): return self.cost < other.cost

    def __ne__(self, other: 'BaseSolution'): return self.cost != other.cost
