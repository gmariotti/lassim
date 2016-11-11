from copy import deepcopy
from typing import List

import numpy as np
import pandas as pd
from PyGMO import champion
from sortedcontainers import SortedDict

from utilities.type_aliases import Vector, Float, Tuple2V

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class Solution:
    """
    Represents the solution of an optimization cycle.
    """

    def __init__(self, champ: champion, react_ids: SortedDict,
                 reactions: Tuple2V):
        self.result = champ
        self.__solution = champ.x
        self.__cost = champ.f[0]
        self.__reactions_ids = react_ids
        self.react_vect, self.react_mask = reactions

    @property
    def cost(self) -> float: return float(self.__cost)

    @property
    def solution_vector(self) -> Vector:
        return np.array(self.__solution, dtype=Float)

    @property
    def number_of_variables(self) -> int: return len(self.__solution)

    def get_solution_matrix(self, headers: List[str]) -> pd.DataFrame:
        """
        Get a numpy matrix representing the solution. Each row of the matrix
        represents a transcription factor, while the columns are divided as
        lambda - vmax - react1 - ... - reactn
        :return: A numpy matrix representing the solution.
        """
        num_tfacts = len(self.reactions_ids.keys())
        lambdas = np.transpose([self.__solution[:num_tfacts]])
        vmax = np.transpose([self.__solution[num_tfacts: 2 * num_tfacts]])
        react_vect = self.react_vect.copy()
        react_vect[self.react_mask] = self.__solution[2 * num_tfacts:]
        react_vect = np.reshape(react_vect, (num_tfacts, num_tfacts))
        lambdas_vmax = np.append(lambdas, vmax, axis=1)
        matrix = np.append(lambdas_vmax, react_vect, axis=1)
        return pd.DataFrame(data=matrix, columns=headers)

    @property
    def reactions_ids(self) -> SortedDict: return deepcopy(self.__reactions_ids)

    def __str__(self):
        solution_string = """
        == Solution info ==
        cost: {}
        decision vector: {}
        reactions: {}
        """
        return solution_string.format(
            self.cost,
            np.array2string(self.solution_vector, separator=","),
            self.reactions_ids
        )

    def __ge__(self, other: 'Solution'): return self.cost >= other.cost

    def __le__(self, other: 'Solution'): return self.cost <= other.cost

    def __eq__(self, other: 'Solution'): return self.cost == other.cost

    def __gt__(self, other: 'Solution'): return self.cost > other.cost

    def __lt__(self, other: 'Solution'): return self.cost < other.cost

    def __ne__(self, other: 'Solution'): return self.cost != other.cost
