from typing import Callable

from sortedcontainers import SortedDict

from core.base_optimization import BaseOptimization
from core.lassim_problem import LassimProblem, LassimProblemFactory
from core.optimizations.differential_evolution import DEOptimization

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class OptimizationFactory:
    """
    Factory class for getting a BaseOptimization reference based on its name.
    Not part of the BaseOptimization class with the purpose of avoiding any
    circular import, that seems to work/not working for no reason at all.
    """
    _optimizations = {
        DEOptimization.type_name: DEOptimization
    }
    _labels = {
        "DE": DEOptimization.type_name
    }

    @classmethod
    def new_optimization_instance(cls, opt_type: str,
                                  prob_builder: LassimProblemFactory,
                                  problem: LassimProblem, reactions: SortedDict,
                                  evolutions: int,
                                  iter_func: Callable[..., bool] = None
                                  ) -> Callable[..., BaseOptimization]:
        if opt_type in cls._optimizations:
            optimization = cls._optimizations[opt_type](
                prob_builder, problem, reactions, evolutions, iter_func
            )
            return optimization.build
        else:
            raise ReferenceError("{} is not a valid option".format(opt_type))

    @classmethod
    def get_optimization_type(cls, short_type: str) -> str:
        if short_type in cls._labels:
            return cls._labels[short_type]
        else:
            raise ReferenceError("{} is not a valid option".format(short_type))
