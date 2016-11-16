from logging import Logger
from typing import Dict, Type, Callable

import psutil

from core.base_solution import BaseSolution
from core.core_system import CoreSystem
from utilities.type_aliases import Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class LassimContext:
    """
    Represents the context of the current optimization. Should allow dependency
    injection of common parameters, like the class that represents the
    solutions, the ode function to use, ..
    """
    def __init__(self, core: CoreSystem, opt_args: 'OptimizationArgs',
                 ode_fun: Callable[..., Vector], pert_fun: Callable[..., float],
                 solution_class: Type[BaseSolution]):
        self.__core = core
        self.__opt_args = opt_args
        self.__ode_function = ode_fun
        self.__pert_function = pert_fun
        self.__solution_class = solution_class

    @property
    def core(self) -> CoreSystem:
        return self.__core

    @property
    def opt_args(self) -> 'OptimizationArgs':
        return self.__opt_args

    @property
    def ode(self) -> Callable[..., Vector]:
        return self.__ode_function

    @property
    def perturbation(self) -> Callable[..., float]:
        return self.__pert_function

    @property
    def SolutionClass(self) -> Type[BaseSolution]:
        return self.__solution_class


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
        self.__cores = num_cores
        self.__islands = self.__cores
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
    def num_cores(self) -> int:
        return self.__cores

    @num_cores.setter
    def num_cores(self, num_cores: int):
        self.__cores = num_cores
        # if the number is less than one, then use all the CPUs available
        if num_cores < 1:
            self.__cores = psutil.cpu_count
        self.__islands = num_cores

    @property
    def num_islands(self) -> int:
        return self.__islands

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
        logger.info("Number of cores is {}".format(self.__cores))
        logger.info("Number of evolutions for archipelago is {}".format(
            self.__evolutions
        ))
        logger.info("Number of individuals for each island is {}".format(
            self.__individuals
        ))
        if is_pert:
            logger.info("Perturbations factor is {}".format(self.__pert_factor))
