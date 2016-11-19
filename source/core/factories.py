from typing import Callable, List

from PyGMO import algorithm
from sortedcontainers import SortedDict

from core.base_optimization import BaseOptimization
from core.lassim_problem import LassimProblem, LassimProblemFactory

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class OptimizationFactory:
    """
    Factory class for getting a BaseOptimization reference based on its name.
    Not part of the BaseOptimization class with the purpose of avoiding any
    circular import, that seems to work/not working for no reason at all.
    """
    # Continuous Unconstrained Single problems
    _labels_cus = {
        # Heuristic
        "DE": algorithm.de,
        "JDE": algorithm.jde,
        "MDE_PBX": algorithm.mde_pbx,
        "DE_1220": algorithm.de_1220,
        "PSO": algorithm.pso,
        "PSO_GEN": algorithm.pso_gen,
        "SGA_GRAY": algorithm.sga_gray,
        "SA_CORANA": algorithm.sa_corana,
        "BEE_COLONY": algorithm.bee_colony,
        "CMAES": algorithm.cmaes
    }

    # They all have default values and they solve
    @classmethod
    def labels_cus(cls) -> List[str]:
        return sorted(set(cls._labels_cus.keys()))

    @classmethod
    def cus_default(cls) -> str:
        return cls.labels_cus()[0]

    @classmethod
    def new_base_optimization(cls, type: str,
                              prob_builder: LassimProblemFactory,
                              problem: LassimProblem, reactions: SortedDict,
                              iter_func: Callable[..., bool] = None
                              ) -> BaseOptimization:
        # raises KeyError if not present
        algo = cls._labels_cus[type]
        return BaseOptimization(
            algo, prob_builder, problem, reactions, iter_func
        )


try:
    # Add Local Optimization algorithms from GSL if PyGMO has been correctly
    # compiled with GSL flag
    gsl_algorithms = {
        "CS": algorithm.cs,
        "GSL_NM": algorithm.gsl_nm,
        "GSL_NM2": algorithm.gsl_nm2,
        "GSL_NM2RAND": algorithm.gsl_nm2rand,
        "GSL_BFGS": algorithm.gsl_bfgs,
        "GSL_BFGS2": algorithm.gsl_bfgs2,
        "GSL_FR": algorithm.gsl_fr,
        "GSL_PR": algorithm.gsl_pr,
    }
    OptimizationFactory._labels_cus.update(gsl_algorithms)
except AttributeError:
    pass
