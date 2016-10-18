from typing import Callable, Dict, Tuple
import psutil

from PyGMO import topology
from sortedcontainers import SortedDict, SortedList

from core.core_problem import CoreProblem, CoreProblemFactory
from core.core_system import CoreSystem
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class BaseOptimization:
    """
    Represents the base class to implement for realizing a new optimization.
    Still undecided if iteration must go there or not.
    """

    def __init__(self, prob_factory: CoreProblemFactory,
                 problem: Tuple[CoreProblem, SortedDict],
                 iter_func: Callable[..., bool]):
        self._probl_factory = prob_factory
        self._start_problem = problem
        self._iterate = iter_func
        self._handler = None
        self._core = None

    def build(self, handler: SolutionsHandler, core: CoreSystem, evols: int,
              **kwargs) -> 'BaseOptimization':
        raise NotImplementedError(self.build.__name__)

    def solve(self, n_threads: int, n_individuals: int,
              topol=topology.unconnected) -> SortedList:
        raise NotImplementedError(self.solve.__name__)

    def print(self):
        raise NotImplementedError(self.print.__name__)


# TODO - similar to a context, consider refactoring
class OptimizationArgs:
    def __init__(self, opt_type: str, params: Dict, num_cores: int,
                 evolutions: int):
        self.type = opt_type
        self.params = params
        self._num_cores = num_cores
        # if the number is less than one, then use all the CPUs available
        if self._num_cores < 1:
            self._num_cores = psutil.cpu_count()
        self.num_islands = self._num_cores
        self.evolutions = evolutions
