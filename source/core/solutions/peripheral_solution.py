from typing import List

import numpy as np
import pandas as pd
from PyGMO.core import champion
from sortedcontainers import SortedDict
from sortedcontainers import SortedSet

from core.base_solution import BaseSolution
from core.problems.network_problem import NetworkProblem

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class PeripheralSolution(BaseSolution):
    """
    Represents the solution of an optimization cycle for a NetworkProblem
    """

    def __init__(self, champ: champion, react_ids: SortedDict,
                 prob: NetworkProblem):
        super(PeripheralSolution, self).__init__(champ, react_ids, prob)
        self.react_vect, self.react_mask = prob.vector_map, prob.vector_map_mask
        self.gene_name = self._get_gene_name()

    def get_solution_matrix(self, headers: List[str]) -> pd.DataFrame:
        """
        Creates a pandas.DataFrame representing the solution of a peripherals
        optimization. The DataFrame has a single row with the format
        [gene_name, lambda, vmax, k1, .., kn]

        :param headers: Name of the columns to use in the DataFrame.
        :return: pandas.DataFrame representing the problem's solution.
        """

        # the number of transcription factors is equal to the number of columns
        # minus lambda and vmax
        num_tfacts = len(headers) - 3
        # FIXME
        # assert self.react_vect.shape[0] / num_tfacts == \
        #        int(self.react_mask.shape[0] / num_tfacts)
        p_lambda = self.solution_vector[0]
        p_vmax = self.solution_vector[1]
        p_react = self.react_vect[num_tfacts * num_tfacts:].copy()
        p_mask = self.react_mask[num_tfacts * num_tfacts:]
        p_react[p_mask] = self.solution_vector[2:]
        p_lambda_vmax = np.array([self.gene_name, p_lambda, p_vmax])
        matrix = np.append(p_lambda_vmax, p_react)
        # FIXME - change DataFrame creation
        return pd.Series(data=matrix, index=headers).to_frame().transpose()

    @property
    def reactions_ids(self) -> SortedSet:
        # FIXME - don't override a SortedDict property with a SortedSet
        return self.reactions_ids[self.gene_name]

    def _get_gene_name(self):
        raise RuntimeError("Monkey patch it!")

    def __ge__(self,
               other: 'PeripheralSolution'): return self.cost >= other.cost

    def __le__(self,
               other: 'PeripheralSolution'): return self.cost <= other.cost

    def __eq__(self,
               other: 'PeripheralSolution'): return self.cost == other.cost

    def __gt__(self, other: 'PeripheralSolution'): return self.cost > other.cost

    def __lt__(self, other: 'PeripheralSolution'): return self.cost < other.cost

    def __ne__(self,
               other: 'PeripheralSolution'): return self.cost != other.cost
