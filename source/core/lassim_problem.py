from typing import List, Tuple

from PyGMO.core import champion
from PyGMO.problem import base

from utilities.type_aliases import Tuple2V, Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class LassimProblem(base):
    """
    Interface of a common LASSIM problem. Every problem that are related to
    LASSIM, should implement it and override the _objfun_impl method.
    """

    def _objfun_impl(self, x):
        raise NotImplementedError(self._objfun_impl.__name__)

    @property
    def champions(self) -> List[champion]:
        _champions = []
        num_best_x = len(self.best_x)
        for i in range(0, num_best_x):
            champ = champion()
            champ.x = self.best_x[i]
            champ.f = self.best_f[i]
            _champions.append(champ)
        return _champions


class LassimProblemFactory:
    """
    Interface of a common factory for building LASSIM problems.
    """

    def build(self, dim: int, bounds: Tuple[List[float], List[float]],
              vector_map: Tuple2V, known_sol: List[Vector], **kwargs):
        raise NotImplementedError(self.build.__name__)
