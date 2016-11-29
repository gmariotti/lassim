import logging
import os
from concurrent.futures import ProcessPoolExecutor
from typing import List, Tuple, Callable, Iterable

from core.base_solution import BaseSolution
from core.utilities.type_aliases import Vector, Tuple3V

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class PlotSerializer:
    def __init__(self, directory: str, fig_names: List[str],
                 axis: List[Tuple[str, str]],
                 gres: Callable[[BaseSolution], Iterable[Tuple3V]],
                 name_creator: Callable[[str, List[str], BaseSolution],
                                        Iterable[str]]):
        self._directory = directory
        self._names = fig_names
        self._axis = axis
        self._res_gen = gres
        self._filename_creator = name_creator

    @classmethod
    def new_instance(cls, output_dir: str, names: List[str],
                     axis: List[Tuple[str, str]],
                     gres: Callable[[BaseSolution], Iterable[Tuple3V]],
                     filename_creator: Callable[[str, List[str], BaseSolution],
                                                Iterable[str]]
                     ) -> 'PlotSerializer':
        """
        Creates a new instance of a PlotSerializer and returns it.
        :param output_dir: Path where to save the plots. If it doesn't exist is
        created automatically.
        :param names: List of names for each plot.
        :param axis: List of tuple containing the names for the x axis and y
        axis. Must be of the same size of names
        :param gres: Function that given as an input a BaseSolution returns
        a tuple containing three np.ndarray for the plotting. First and second
        return values must be the data to represent, the third value the time
        sequence.
        :param filename_creator: A creator of an iterator for unique names for
        each plot file.
        :return: A PlotSerializer instance.
        """
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        if len(axis) != len(names):
            raise ValueError("List of axis must have same size of names")
        return PlotSerializer(
            output_dir, names, axis, gres, filename_creator
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

        # runs it on a different process in order to avoid problem if plotting
        # is not done on main thread
        with ProcessPoolExecutor() as pool:
            idx = 0
            futures = []
            for data, results, time in self._res_gen(solution):
                futures.append(pool.submit(
                    plotting_function, data, results, time, self._axis[idx][0],
                    self._axis[idx][1], figures_names[idx])
                )
                # out of bound check, avoids exception
                idx += 1
                if idx >= len(self._axis):
                    break
            # wait maximum 10 seconds for completion off each future otherwise
            # a TimeoutError is raised
            for future in futures:
                future.result(timeout=100)


def plotting_function(data: Vector, results: Vector, time: Vector, x_label: str,
                      y_label: str, figure_name: str):
    try:
        # to do in order to avoid the use of an X-server. For more info look at
        # http://stackoverflow.com/questions/4706451/how-to-save-a-figure-remotely-with-pylab/4706614#4706614
        import matplotlib
        matplotlib.use("Agg")

        import matplotlib.pyplot as plt
        plt.figure()
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.plot(time, data, label="data")
        plt.plot(time, results, label="results")
        plt.legend()
        plt.savefig(figure_name)
        plt.close()
    except Exception:
        logging.getLogger(__name__).exception("Matplotlib exception")
