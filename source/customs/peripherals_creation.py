import logging
from typing import Tuple, Iterable, List, Optional

import numpy as np
import pandas as pd
from sortedcontainers import SortedDict, SortedSet

from core.lassim_context import LassimContext
from core.lassim_network import NetworkSystem, CoreSystem
from core.problems.network_problem import NetworkProblemFactory, NetworkProblem
from core.utilities.type_aliases import Vector, Tuple2V, Float
from customs.peripherals_functions import default_bounds, \
    generate_reactions_vector, generate_core_vector
from data_management.csv_format import parse_core_data, \
    parse_peripherals_network, parse_perturbations_data, parse_patient_data, \
    parse_time_sequence, parse_y0_data
from utilities.data_classes import PeripheralsData, InputFiles, InputExtra, \
    CoreData

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
    network = parse_peripherals_network(network_file)

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


def parse_peripherals_data(network: NetworkSystem, files: InputFiles,
                           extra: InputExtra, core_data: pd.DataFrame
                           ) -> Iterable[Tuple[str, PeripheralsData]]:
    """
    Parses the data for the peripherals. For performance reasons, the method
    returns a generator.

    :param network: Instance of NetworkSystem representing the current network.
    :param files: InputFiles to use.
    :param extra: InputExtra for other options/files.
    :param core_data: pandas.DataFrame with the data of the core.
    :return: A generator that produces a tuple containing as first element the
        name of the gene, and as second element an instance of PeripheralsData
        with the data for that gene.
    :raise AttributeError: If the transcription factors in the network are not
        the same as the ones in the peripherals data and/or the perturbations
        data, if present.
    """

    logger = logging.getLogger(__name__)
    core_perturbations = parse_perturbations_data(extra.core_pert)
    gene_datas = [parse_patient_data(filename) for filename in files.data]

    tfacts = [tfact for tfact in network.core.tfacts]
    for data in gene_datas:
        data_tfacts = data.index.values.tolist()
        if tfacts != data_tfacts:
            message = "Transcription factors in the data are different from " \
                      "the one in the network."
            logger.error(message)
            logger.error("Data {}".format(data_tfacts))
            logger.error("Network {}".format(tfacts))
            raise AttributeError(message)

    # tries to parse the perturbations data. If an OSError is raised, usually
    # for a missing file, the perturbations data are assumed not present.
    genes_perturbations = check_genes_perturbations(files, tfacts)

    times = parse_time_sequence(files.times)
    for gene, reactions in network.reactions.viewitems():
        try:
            gene_data, gene_sigma = parse_peripheral_data(gene_datas, gene)
        except KeyError:
            logger.error("Searched for gene {} in data but not found."
                         "Will be skipped".format(gene))
            continue

        gene_pert = None
        if genes_perturbations is not None:
            try:
                gene_pert = genes_perturbations.ix[gene].values
            except KeyError:
                logger.error("Searched for gene {} in perturbations but not "
                             "present. Will be skipped".format(gene))
                continue
        y0 = set_ode_y0(gene_data, extra, core_data)
        cdata = CoreData(
            gene_data, gene_sigma, times.copy(), core_perturbations.copy(), y0
        )
        pdata = PeripheralsData(cdata, gene_pert, 1, len(reactions), reactions)
        yield gene, pdata


def check_genes_perturbations(files: InputFiles, tfacts: List[str]
                              ) -> Optional[pd.DataFrame]:
    """
    Tries to parse the perturbations file if present and compares the columns
    in it with the list of excepted transcription factors.

    :param files: InputFiles instance where to find the path to the
        perturbations file.
    :param tfacts: List of transcription factors expected.
    :return: None if the file doesn't exist, otherwise the pandas.DataFrame
        containing the perturbations data with the list of genes as index.
    :raise AttributeError: If the transcription factors in the perturbations
        file are not the same as the one expected.
    """

    logger = logging.getLogger(__name__)
    try:
        genes_perturbations = parse_perturbations_data(
            files.perturbations, check_times=False
        ).set_index(["source"], verify_integrity=True)
    except OSError:
        genes_perturbations = None

    # check that the transcription factors in genes_perturbations are the same
    # of the core system
    if genes_perturbations is not None:
        # doesn't need to drop the source column because is at the index now.
        pert_columns = genes_perturbations.columns.value.tolist()
        if pert_columns != tfacts:
            message = "Transcription factors in the perturbations are " \
                      "different from the one in the network."
            logger.error(message)
            logger.error("Perturbations {}".format(pert_columns))
            logger.error("Transcription factors {}".format(tfacts))
            raise AttributeError(message + " Check log for more info.")

    return genes_perturbations


def parse_peripheral_data(data_list: List[pd.DataFrame], gene_name: str
                          ) -> Tuple2V:
    """
    Parses the patient data for the corresponding gene.

    :param data_list: List of patient data containing the gene.
    :param gene_name: The name of the gene to search.
    :return: A data Vector normalized and with the mean of the data passed in
        the list and its standard deviation.
    """

    gene_data = np.array(
        [data.ix[gene_name].values for data in data_list], dtype=Float
    )
    # axis = 1 gives the maximum for each row
    norm_data = (gene_data.T / np.amax(gene_data, axis=1)).T
    # axis = 0 gives the mean for each column
    data_mean = norm_data.mean(axis=0)
    std_dev = norm_data.std(axis=0)

    return data_mean, std_dev


def set_ode_y0(gene_data: Vector, extra: InputExtra, core_data: pd.DataFrame
               ) -> Vector:
    """
    Creates a vector with the starting points for the ODE system.

    :param gene_data: Vector containing the data for the gene.
    :param extra: InputExtra instance with the name of the y0 file for the core.
    :param core_data: Data of the core.
    :return: Vector containing the value at time 0 of transcription factors and
        gene in the following way:
        [tf_1,..,tf_n, g]
    """

    core_y0 = parse_y0_data(core_data, extra)
    gene_y0 = gene_data[0]
    return np.array(core_y0.tolist() + gene_y0.tolist, dtype=Float)


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
