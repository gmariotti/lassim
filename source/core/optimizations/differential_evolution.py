import logging
from inspect import signature
from typing import Callable, Dict

from PyGMO import algorithm
from sortedcontainers import SortedDict

from core.base_optimization import BaseOptimization
from core.core_system import CoreSystem
from core.lassim_problem import LassimProblemFactory, LassimProblem
from core.solutions_handler import SolutionsHandler

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class DEOptimization(BaseOptimization):
    """
    Implementation of the BaseOptimization class for using the classic
    Differential Evolution algorithm, as implemented and described in
    PyGMO.algorithm.de
    """

    type_name = "Differential Evolution"

    def __init__(self, prob_factory: LassimProblemFactory,
                 problem: LassimProblem, reactions: SortedDict, evolutions: int,
                 iter_func: Callable[..., bool]):
        super(DEOptimization, self).__init__(
            prob_factory, problem, reactions, iter_func
        )
        # default settings for algorithm
        self._algorithm = algorithm.de()
        self._logger = logging.getLogger(__name__)
        self._evolutions = evolutions

        # can be useful to save all the archipelagos used for each optimization
        # FIXME
        # self._archipelagos = SortedList()

    def build(self, handler: SolutionsHandler, core: CoreSystem,
              **kwargs) -> 'DEOptimization':
        de_opt = DEOptimization(
            self._probl_factory, self._start_problem, self._start_reactions,
            self._evolutions, self._iterate
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
        """
        Based on the <key:value> pairs in kwargs, discriminates between valid
        and invalid arguments based on the signature of algorithm.de.
        :param kwargs: <key:value> pair for the optimization algorithm
        :return: Dictionary with <key:value> valid for algorithm.de
        """
        arguments = signature(algorithm.de.__init__).parameters
        valid_found = {}
        for arg in arguments:
            if arg in kwargs:
                valid_found[arg] = kwargs[arg]
        return valid_found

    def print(self):
        super(DEOptimization, self).print()
