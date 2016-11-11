from typing import List, Tuple

from PyGMO.problem import base

from utilities.type_aliases import Tuple2V, Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class LassimProblem(base):
    """
    Interface of a common LASSIM problem. Every problem that are related to
    LASSIM, should implement it.
    """

    def _objfun_impl(self, x):
        raise NotImplementedError(self._objfun_impl.__name__)

    def plot(self, decision_vector: Vector, figure_name: List[str],
             x_label: str, y_label: str):
        raise NotImplementedError(self.plot.__name__)


class LassimProblemFactory:
    """
    Interface of a common factory for building LASSIM problems.
    """

    def build(self, dim: int, bounds: Tuple[List[float], List[float]],
              vector_map: Tuple2V):
        raise NotImplementedError(self.build.__name__)
