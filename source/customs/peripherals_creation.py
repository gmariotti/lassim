from typing import Tuple

import logging
import pandas as pd
from sortedcontainers import SortedDict, SortedSet

from core.lassim_context import LassimContext
from core.lassim_network import NetworkSystem, CoreSystem
from core.problems.network_problem import NetworkProblemFactory, NetworkProblem
from core.utilities.type_aliases import PeripheralsData
from customs.peripherals_functions import default_bounds, \
    generate_reactions_vector, generate_core_vector
from data_management.csv_format import parse_core_data, parse_network

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

"""
Set of custom functions for handling the peripherals problem creation and
its general setup.
"""


def create_network(network_file: str, core_file: str) -> NetworkSystem:
    """
    Creates a NetworkSystem instance starting from its network file and the
    a file containing the data for the core.

    :param network_file: Path to the file containing the network info.
    :param core_file: Path to the file containing the core data.
    :return: NetworkSystem instance representing the given core and the
        corresponding network given as input.
    """

    core_data = parse_core_data(core_file)
    reactions = get_reactions_from_data(core_data)
    core = CoreSystem.generate_core(reactions)
    network = parse_network(network_file)

    return NetworkSystem(network, core)


def get_reactions_from_data(core_data: pd.DataFrame) -> SortedDict:
    """
    From a pandas.DataFrame extracts the map of reactions for each transcription
    factor. Is fundamental that the core_data has the headers lambda and vmax,
    and that missing reactions have value 0.

    :param core_data: pandas.DataFrame representing the data from a core.
    :return: SortedDict with values as <tfact:set(tfacts)>.
    """

    reactions = SortedDict()
    data = core_data.drop(["lambda", "vmax"], axis=1)
    columns = [*data.columns]
    for index, row in data.iterrows():
        series = row.mask(lambda x: x == 0).dropna()
        reactions[columns[index]] = SortedSet(*series.axes)

    return reactions


def problem_setup(gene_data: PeripheralsData, context: LassimContext
                  ) -> Tuple[NetworkProblemFactory, NetworkProblem]:
    """
    Function for the setup of the problem. Used for creating the problem
    factory and the starting problem to solve.

    :param gene_data: Instance of PeripheralsData. Should be related to just
        a single gene.
    :param context: LassimContext for solving this problem.
    :return: Tuple containing a NetworkProblemFactory instance and a starting
        NetworkProblem instance to solve.
    """

    core_data = gene_data.core_data
    core_net = context.network.core
    if core_data.perturb is None:
        factory = NetworkProblemFactory.new_instance(
            (core_data.data, core_data.sigma, core_data.times),
            core_data.y0, context.ode
        )
        logging.getLogger(__name__).info(
            "Built factory for problem without perturbations..."
        )
    else:
        factory = NetworkProblemFactory.new_instance(
            (core_data.data, core_data.sigma, core_data.times,
             core_data.perturb, gene_data.pert_gene), core_data.y0,
            context.ode, context.perturbation,
            context.primary_first.pert_factor
        )
        logging.getLogger(__name__).info(
            "Built factory for problem with perturbations..."
        )

    start_problem = factory.build(
        dim=(gene_data.num_genes * 2 + gene_data.num_react),
        bounds=default_bounds(gene_data.num_genes, gene_data.num_react),
        vector_map=generate_reactions_vector(
            gene_data.reactions, core_data.data
        ), core_data=generate_core_vector(
            core_data.data, core_net.num_tfacts, gene_data.react_count,
            gene_data.reactions
        ))

    return factory, start_problem
