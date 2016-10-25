from typing import Callable, Tuple

from PyGMO import topology
from sortedcontainers import SortedDict, SortedList

from core.base_optimization import BaseOptimization
from core.core_problem import LassimProblemFactory, LassimProblem
from core.core_system import CoreSystem
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class BHOptimization(BaseOptimization):
    type_name = "BasinHopping"

    def __init__(self, prob_factory: LassimProblemFactory,
                 problem: Tuple[LassimProblem, SortedDict],
                 iter_func: Callable[..., bool]):
        super().__init__(prob_factory, problem, iter_func)
        raise NotImplementedError(self.__init__.__name__)

    def build(self, handler: SolutionsHandler, core: CoreSystem, evols: int,
              **kwargs) -> 'BaseOptimization':
        raise NotImplementedError(self.build.__name__)

    def solve(self, n_threads: int, n_individuals: int,
              topol=topology.unconnected) -> SortedList:
        raise NotImplementedError(self.solve.__name__)

    def print(self):
        raise NotImplementedError(self.print.__name__)
