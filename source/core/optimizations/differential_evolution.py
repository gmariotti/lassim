import logging
from inspect import signature
from typing import Callable, Dict, Tuple

from PyGMO import algorithm, topology, archipelago
from sortedcontainers import SortedDict, SortedList, SortedListWithKey

from core.base_optimization import BaseOptimization
from core.core_system import CoreSystem
from core.lassim_problem import LassimProblemFactory, LassimProblem
from core.solution import Solution
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class DEOptimization(BaseOptimization):
    """
    Represents an implementation of the BaseOptimization class for the
    Differential Evolution algorithms offered by PyGMO.algorithm
    """

    type_name = "Differential Evolution"

    def __init__(self, prob_factory: LassimProblemFactory,
                 problem: Tuple[LassimProblem, SortedDict], evolutions: int,
                 iter_func: Callable[..., bool]):
        super(DEOptimization, self).__init__(prob_factory, problem, iter_func)
        # default settings for algorithm
        self._algorithm = algorithm.de()
        self._logger = logging.getLogger(__name__)
        self._evol = evolutions

        # can be useful to save all the archipelagos used for each optimization
        # FIXME
        # self._archipelagos = SortedList()

    def build(self, handler: SolutionsHandler, core: CoreSystem,
              **kwargs) -> 'DEOptimization':
        de_opt = DEOptimization(
            self._probl_factory, self._start_problem, self._evol, self._iterate
        )
        valid_args = self.verify_arguments(**kwargs)
        if len(valid_args) > 0:
            de_opt._algorithm = algorithm.de(**valid_args)
            de_opt._logger.info("Arguments for {} are:\n{}".format(
                self.type_name, valid_args
            ))
        de_opt._handler = handler
        de_opt._core = core
        return de_opt

    def verify_arguments(self, **kwargs) -> Dict:
        arguments = signature(algorithm.de.__init__).parameters
        valid_found = {}
        for arg in arguments:
            if arg in kwargs:
                valid_found[arg] = kwargs[arg]
        return valid_found

    def print(self):
        super(DEOptimization, self).print()
