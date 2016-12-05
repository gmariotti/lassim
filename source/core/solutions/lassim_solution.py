from typing import List

import numpy as np
import pandas as pd
from PyGMO.core import champion
from sortedcontainers import SortedDict

from core.base_solution import BaseSolution
from core.problems.core_problem import CoreProblem

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class LassimSolution(BaseSolution):
    """
    Represents the solution of an optimization cycle for the Lassim Problem.
    """

    def __init__(self, champ: champion, react_ids: SortedDict,
                 prob: CoreProblem):
        super(LassimSolution, self).__init__(champ, react_ids, prob)
        self.react_vect, self.react_mask = prob.vector_map, prob.vector_map_mask

    def get_solution_matrix(self, headers: List[str]) -> pd.DataFrame:
        """
        Get a numpy matrix representing the solution. Each row of the matrix
        represents a transcription factor, while the columns are divided as
        lambda - vmax - react1 - ... - reactn
        :return: A numpy matrix representing the solution.
        """
        num_tfacts = len(self.reactions_ids.keys())
        lambdas = np.transpose([self._solution[:num_tfacts]])
        vmax = np.transpose([self._solution[num_tfacts: 2 * num_tfacts]])
        react_vect = self.react_vect.copy()
        react_vect[self.react_mask] = self._solution[2 * num_tfacts:]
        react_vect = np.reshape(react_vect, (num_tfacts, num_tfacts))
        lambdas_vmax = np.append(lambdas, vmax, axis=1)
        matrix = np.append(lambdas_vmax, react_vect, axis=1)
        return pd.DataFrame(data=matrix, columns=headers)

    def __ge__(self, other: 'LassimSolution'): return self.cost >= other.cost

    def __le__(self, other: 'LassimSolution'): return self.cost <= other.cost

    def __eq__(self, other: 'LassimSolution'): return self.cost == other.cost

    def __gt__(self, other: 'LassimSolution'): return self.cost > other.cost

    def __lt__(self, other: 'LassimSolution'): return self.cost < other.cost

    def __ne__(self, other: 'LassimSolution'): return self.cost != other.cost
