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
        """
        Creates a new instance of a PlotSerializer and returns it.
        :param output_dir: Path where to save the plots. If it doesn't exist is
        created automatically.
        :param names: List of names for each plot.
        :param axis: List of tuple containing the names for the x axis and y
        axis. Must be of the same size of names
        :param res_ode: Function that given as an input a BaseSolution returns
        a tuple containing three np.ndarray for the plotting. First and second
        return values must be the data to represent, the third value the time
        sequence.
        :param filename_creator: A creator of an unique name for each plot file.
        :return: A PlotSerializer instance.
        """
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        if len(axis) != len(names):
            raise ValueError("List of axis must have same size of names")
        return PlotSerializer(
            output_dir, names, axis, res_ode, filename_creator
        )

    def serialize_solution(self, solution: BaseSolution, directory: str = None):
        """
        Plotting of a BaseSolution using the data received at instantiation time
        and the results from the ODE function passed.
        :param solution: a BaseSolution instance, doesn't matter how data are
        represented.
        :param directory: Optional value in case plots have to be saved in
        another directory.
        """
        outdir = self._directory
        if directory is not None and os.path.isdir(directory):
            os.makedirs(directory)
            outdir = directory
        generator = self._filename_creator(outdir, self._names, solution)
        figures_names = [name for name in generator]
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
            # out of bound check, avoid exception
            idx += 1
            if idx >= len(self._axis):
                break
