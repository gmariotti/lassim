import os
from typing import List, Tuple, Callable

import matplotlib.pyplot as plt

from core.base_solution import BaseSolution
from utilities.type_aliases import Tuple3V

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class PlotSerializer:
    def __init__(self, directory: str, fig_names: List[str],
                 axis: List[Tuple[str, str]],
                 res_ode: Callable[[BaseSolution], Tuple3V],
                 name_creator: Callable[[str, List[str], BaseSolution], str]):
        self._directory = directory
        self._names = fig_names
        self._axis = axis
        self._res_ode = res_ode
        self._filename_creator = name_creator

    @classmethod
    def new_instance(cls, output_dir: str, names: List[str],
                     axis: List[Tuple[str, str]],
                     res_ode: Callable[[BaseSolution], Tuple3V],
                     filename_creator: Callable[
                         [str, List[str], BaseSolution], str]
                     ) -> 'PlotSerializer':
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        if len(axis) != len(names):
            raise ValueError("List of axis must have same size of names")
        return PlotSerializer(
            output_dir, names, axis, res_ode, filename_creator
        )

    def serialize_solution(self, solution: BaseSolution, directory: str = None):
        outdir = self._directory
        if directory is not None and os.path.isdir(directory):
            os.makedirs(directory)
            outdir = directory
        generator = self._filename_creator(outdir, self._names, solution)
        figures_names = [name for name in generator]
        # TODO - how to handle case for out of bound??
        idx = 0
        for data, results, time in self._res_ode(solution):
            plt.figure()
            plt.xlabel(self._axis[idx][0])
            plt.ylabel(self._axis[idx][1])
            plt.plot(time, data, label="data")
            plt.plot(time, results, label="results")
            plt.legend()
            plt.savefig(figures_names[idx])
            plt.close()
            idx += 1
