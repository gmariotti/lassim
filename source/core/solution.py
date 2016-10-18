from copy import deepcopy
from typing import Tuple

import numpy as np
from PyGMO import champion
from sortedcontainers import SortedDict

from utilities.type_aliases import Vector, Float

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class Solution:
    """
    Represents the solution of an optimization cycle.
    """

    def __init__(self, champ: champion, react_ids: SortedDict,
                 reactions: Tuple[Vector, Vector]):
        self.result = champ
        self.solution = champ.x
        self.cost = champ.f[0]
        self.reactions_ids = react_ids
        self.react_vect, self.react_mask = reactions

    def get_cost(self) -> float:
        """
        Get the cost of this solution as a float number.
        :return: The solution cost casted to python float
        """
        return float(self.cost)

    def get_solution_vector(self) -> Vector:
        """
        Get the decision vector for this solution.
        :return: The decision vector as a numpy array.
        """
        return np.array(self.solution, dtype=Float)

    def get_number_of_variables(self) -> int:
        """
        Get the number of variables in the decision vector.
        :return: The number of variables in the decision vector.
        """
        return len(self.solution)

    def get_solution_matrix(self) -> Vector:
        """
        Get a numpy matrix representing the solution. Each row of the matrix
        represents a transcription factor, while the columns are divided as
        lambda - vmax - react1 - ... - reactn
        :return: A numpy matrix representing the solution.
        """
        num_tfacts = len(self.reactions_ids.keys())
        lambdas = np.transpose([self.solution[:num_tfacts]])
        vmax = np.transpose([self.solution[num_tfacts: 2 * num_tfacts]])
        react_vect = self.react_vect.copy()
        react_vect[self.react_mask] = self.solution[2 * num_tfacts:]
        react_vect = np.reshape(react_vect, (num_tfacts, num_tfacts))
        lambdas_vmax = np.append(lambdas, vmax, axis=1)
        return np.append(lambdas_vmax, react_vect, axis=1)

    def get_reactions_ids(self) -> SortedDict:
        """
        Gets a deep copy of the reactions ids dictionary
        :return: reactions ids copy
        """
        return deepcopy(self.reactions_ids)
