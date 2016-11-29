from typing import Callable, List

from PyGMO import algorithm
from sortedcontainers import SortedDict

from core.base_optimization import BaseOptimization
from core.lassim_problem import LassimProblem, LassimProblemFactory
# from core.optimizations.multi_start_optimization import MultiStartOptimization

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
    # algorithms for solving Continuous Unconstrained Single problems
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
    def new_base_optimization(cls, o_type: str, p_builder: LassimProblemFactory,
                              prob: LassimProblem, reactions: SortedDict,
                              iter_func: Callable[..., bool] = None
                              ) -> BaseOptimization:
        """
        Factory method for creation of a BaseOptimization object.
        :param o_type: The label of an valid optimization algorithm.
        :param p_builder: A factory for building a LassimProblem instance.
        :param prob: The LassimProblem instance to solve at first.
        :param reactions: The dictionary with the reactions associated to the
        LassimProblem
        :param iter_func: An optional iteration function to run after each
        completed optimization. Use it in order to dynamically change the
        problem to solve and its reactions.
        :return: An instance of BaseOptimization.
        """
        # raises KeyError if not present
        algo = cls._labels_cus[o_type]
        return BaseOptimization(
            algo, p_builder, prob, reactions, iter_func
        )

    # @classmethod
    # def new_multistart_optimization(cls, o_type: str,
    #                                 p_builder: LassimProblemFactory,
    #                                 problem: LassimProblem,
    #                                 reactions: SortedDict,
    #                                 iter_func: Callable[..., bool],
    #                                 sec_type: str) -> MultiStartOptimization:
    #     """
    #     TODO
    #     :param o_type:
    #     :param p_builder:
    #     :param problem:
    #     :param reactions:
    #     :param iter_func:
    #     :param sec_type:
    #     :return:
    #     """
    #     # raises KeyError if not present
    #     main_algo = cls._labels_cus[o_type]
    #     sec_algo = cls._labels_cus[sec_type]
    #     return MultiStartOptimization(
    #         main_algo, sec_algo, p_builder, problem, reactions, iter_func
    #     )


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
