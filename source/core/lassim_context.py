from logging import Logger
from typing import Dict, Type, Callable, List, Optional

import psutil

from core.base_solution import BaseSolution
from core.core_system import CoreSystem
from core.utilities.type_aliases import Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class LassimContext:
    """
    Represents the context of the current optimization. Should allow dependency
    injection of common parameters, like the class that represents the
    solutions, the ode function to use, ..
    """

    def __init__(self, core: CoreSystem, primary_opt: List['OptimizationArgs'],
                 ode_fun: Callable[..., Vector], pert_fun: Callable[..., float],
                 solution_class: Type[BaseSolution],
                 secondary_opt: List['OptimizationArgs'] = None):
        self.__core_system = core
        if len(primary_opt) == 0:
            raise ValueError("Primary optimization list can't be empty")
        self.__primary_opt = primary_opt
        self.__ode_function = ode_fun
        self.__pert_function = pert_fun
        self.__solution_class = solution_class
        self.__secondary_opt = list()
        if secondary_opt is not None:
            self.__secondary_opt = secondary_opt

    @property
    def core(self) -> CoreSystem:
        return self.__core_system

    @property
    def primary_opts(self) -> List['OptimizationArgs']:
        # recreate the list in order to not allowing the possibility to modify
        # the main one
        return [val for val in self.__primary_opt]

    @property
    def primary_first(self) -> 'OptimizationArgs':
        return self.primary_opts[0]

    @property
    def secondary_opts(self) -> List['OptimizationArgs']:
        return [val for val in self.__secondary_opt]

    # FIXME - use my Optional
    @property
    def secondary_first(self) -> Optional['OptimizationArgs']:
        if len(self.secondary_opts) > 0:
            return self.secondary_opts[0]
        else:
            return None

    @property
    def ode(self) -> Callable[..., Vector]:
        return self.__ode_function

    @property
    def perturbation(self) -> Callable[..., float]:
        return self.__pert_function

    @property
    def SolutionClass(self) -> Type[BaseSolution]:
        return self.__solution_class

    def __str__(self) -> str:
        # TODO
        return "LassimContext"

    __repr__ = __str__


class OptimizationArgs:
    """
    This class represents the list of arguments for an optimization. Except for
    the number of cores, each argument is read-only and is initialized at class
    instantiation.
    """

    def __init__(self, opt_type: str, params: Dict, num_cores: int,
                 evolutions: int, individuals: int, pert_factor: float):
        self.__type = opt_type
        self.__params = params
        self.__islands = num_cores
        self.__evolutions = evolutions
        self.__individuals = individuals
        self.__pert_factor = pert_factor

    @property
    def type(self) -> str:
        return self.__type

    @property
    def params(self) -> Dict:
        return self.__params

    @property
    def num_islands(self) -> int:
        return self.__islands

    @num_islands.setter
    def num_islands(self, num_islands: int):
        # if the number is less than one, then use all the CPUs available
        if num_islands < 1:
            self.__islands = psutil.cpu_count
        self.__islands = num_islands

    @property
    def num_evolutions(self) -> int:
        return self.__evolutions

    @property
    def num_individuals(self) -> int:
        return self.__individuals

    @property
    def pert_factor(self) -> float:
        return self.__pert_factor

    def log_args(self, logger: Logger, is_pert: bool = False):
        """
        Used to log the optimization arguments inserted by the user.
        :param logger: the logging object to use
        :param is_pert: if the presence of the perturbations factor has to be
        logged or not.
        """
        logger.info("Algorithm used is {}".format(self.__type))
        logger.info("Number of cores is {}".format(self.__islands))
        logger.info("Number of evolutions for archipelago is {}".format(
            self.__evolutions
        ))
        logger.info("Number of individuals for each island is {}".format(
            self.__individuals
        ))
        if is_pert:
            logger.info("Perturbations factor is {}".format(self.__pert_factor))
