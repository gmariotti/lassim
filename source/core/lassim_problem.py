from typing import List, Tuple

from PyGMO.problem import base

from utilities.type_aliases import Tuple2V


class LassimProblem(base):
    """
    Interface of a common LASSIM problem. Every problem that are related to
    LASSIM, should implement it.
    """

    def _objfun_impl(self, x):
        raise NotImplementedError(self._objfun_impl.__name__)


class LassimProblemFactory:
    """
    Interface of a common factory for building LASSIM problems.
    """

    def build(self, dim: int, bounds: Tuple[List[float], List[float]],
              vector_map: Tuple2V):
        raise NotImplementedError(self.build.__name__)
