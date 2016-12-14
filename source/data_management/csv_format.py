import logging

import numpy as np
import pandas as pd
from sortedcontainers import SortedSet, SortedDict

from core.utilities.type_aliases import Float, Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def parse_network(filename: str, sep: str = "\t") -> SortedDict:
    """
    Parses data from a network file. The file must contain the headers 'source'
    for the name of the transcription factor and 'target' for the name of
    the transcription factor/gene on which it has influence.

    :param filename: Name of the network file.
    :param sep: Separator used in the file. Default is \t (tab).
    :return: A SortedDict with each pair as <tf:set(tf/genes)>
    :raise AttributeError: TODO
    :raise OSError: If the file doesn't exist.
    """

    # expected headers in a network file
    h_source = "source"
    h_target = "target"

    net_file = pd.read_csv(filename, sep=sep)
    network = SortedDict()
    if not {h_source, h_target}.issubset(net_file.columns):
        logging.getLogger(__name__).error(
            "Missing headers {} and/or {} in {}".format(
                h_source, h_target, filename
            ))
        raise AttributeError("Not valid network headers, check log.")

    for (index, series) in net_file.iterrows():
        target = series[h_target]
        source = series[h_source]
        if source not in network.keys():
            network[source] = SortedSet()
        network[source].add(target)

    return network


def parse_patient_data(filename: str, sep: str = "\t") -> pd.DataFrame:
    """
    The patient data must be a 'sep' separated file with the following headers
    ["source", "t0", "t1", ..., "tn"].

    :param filename: Path of the patient file.
    :param sep: Separator used in the file. Default is \t (tab).
    :return: pandas.DataFrame with the name of the transcription factors as
        index. The DataFrame is ordered by name.
    :raise AttributeError: If the header "source" is missing or if the sequence
        of <t0,..,tn> is not right.
    :raise OSError: If the file doesn't exist.
    """

    # expected headers in a network data file
    h_source = "source"

    data = pd.read_csv(filename, sep=sep)
    if h_source not in data.columns:
        logging.getLogger(__name__).error(
            "Missing header {} in {}".format(h_source, filename)
        )
        raise AttributeError("Not valid data headers, check log.")

    # check that the correct time headers are present
    columns = len(data.columns)
    valid_t_headers = set(["t{}".format(i) for i in range(0, columns - 1)])
    if not valid_t_headers.issubset(data.columns):
        logging.getLogger(__name__).error(
            "Expected headers for time are {}".format(valid_t_headers)
        )
        raise AttributeError("Not valid data headers, check log.")

    data.set_index(h_source, inplace=True, verify_integrity=True)

    return data.sort_index()


def parse_time_sequence(filename: str, sep: str = "\t",
                        d_type: np.dtype = Float) -> Vector:
    """
    The time sequence must be a 'sep' separated file with the following headers
    ["t0", "t1", ..., "tn"].

    :param filename: Path to the file containing the time sequence on which the
        data has been analyzed.
    :param sep: Separator used in the file. Default is \t (tab).
    :param d_type: Type to use for numpy array.
    :return: Vector with the value starting from t0 to tn.
    :raise AttributeError: TODO
    :raise OSError: If the file doesn't exist.
    """

    times = pd.read_csv(filename, sep=sep)
    # check validity of headers
    num_columns = len(times.columns)
    valid_headers = set(["t{}".format(i) for i in range(0, num_columns)])
    if not valid_headers.issubset(times.columns):
        logging.getLogger(__name__).error(
            "Expected headers for time series are {}".format(valid_headers)
        )
        raise AttributeError("Not valid time series headers, check log.")

    return np.array(times.values, dtype=d_type).flatten()


def parse_perturbations_data(filename: str, sep: str = "\t",
                             check_times: bool = True) -> pd.DataFrame:
    """
    The perturbations files must be a 'sep' separated file with the following
    headers: ["<source1>, ..., "<source_n>", "t_start", "t_end"]

    :param filename: Path to the file containing the perturbations data.
    :param sep: Separator used in the file. Default is \t (tab).
    :param check_times: Boolean value to use for checking the presence or not of
        headers "t_start" and "t_end". Default is True.
    :return: The pandas.DataFrame containing the perturbations data. The values
        are a #source * #source matrix representing the perturbation data for
        each source with the others. Each column represent how each of its
        element changes when the column source is modified.
    :raise AttributeError: If check_times is True and the headers "t_start"
        and "t_end" are missing.
    :raise OSError: If the file doesn't exist.
    """

    perturbations = pd.read_csv(filename, sep=sep)

    if check_times:
        # check validity of times headers
        h_tstart = "t_start"
        h_tend = "t_end"
        start_idx = len(perturbations.columns) - 2
        # takes the list of the last two headers
        headers = set(perturbations.ix[:, start_idx:].columns)
        valid_headers = {h_tstart, h_tend}
        if headers != valid_headers:
            # they are not the same set
            logging.getLogger(__name__).error(
                "Expected last two headers for perturbations are {}".format(
                    valid_headers
                ))
            raise AttributeError("Not valid perturbations headers, check log.")

    return perturbations


def parse_peripherals_network(filename: str, sep: str = "\t") -> SortedDict:
    """
    The peripherals network must be a file with the following headers:
    ["source", <tfact_1>,..,<tfact_n>].
    In the source columns must be present the name of the gene, while in the
    <tfact_n> columns must be present 1 if the gene is regulated by <tfact_n>,
    0 if not and NaN if don't know.

    :param filename: Path to the file containing the data of a peripherals
        network.
    :param sep: Separator used in the file. Default is \t (tab)
    :return: SortedDict with pairs as <gene: set(tfacts)>.
    :raise AttributeError: if header "source" is missing.
    :raise OSError: If the file doesn't exist.
    """

    h_source = "source"

    network = pd.read_csv(filename, sep=sep)
    if h_source not in network:
        logging.getLogger(__name__).error(
            "Missing header {} in {}".format(h_source, filename))
        raise AttributeError("Not valid network headers, check log.")

    network.set_index("source", inplace=True, verify_integrity=True)
    # NaN values are set to 1
    network.fillna(1, inplace=True)
    # evaluates values % 2. 1 is mapped to True, 0 to False.
    # In this way if some asshole decides to not use 1 and 0, well, it'll be
    # fucked.
    bool_network = network.applymap(lambda x: x % 2 == 1)
    network_dict = SortedDict({
        index: SortedSet(series[series == True].index.values.tolist())
        for index, series in bool_network.iterrows()
    })
    return network_dict


def parse_core_data(filename: str, sep: str = "\t") -> pd.DataFrame:
    """
    The core files must be a tabular file with the following headers
    ["lambda", "vmax", "<tfact_1>",...,"<tfact_n>"].

    :param filename: Path to the file containing the data of a core system.
    :param sep: Separator used in the file. Default is \t (tab).
    :return: pandas.DataFrame with same columns as the input file plus a'source'
        column containing the corresponding transcription factor for each row.
    :raise AttributeError: if headers "lambda" and "vmax" are missing or
        if the reactions are not a n*n matrix.
    :raise OSError: If the file doesn't exist.
    """

    core_data = pd.read_csv(filename, sep=sep, dtype=Float)
    columns = core_data.columns
    first_headers = {"lambda", "vmax"}
    logger = logging.getLogger(__name__)
    if not first_headers.issubset({*columns}):
        logger.error(
            "Expected the following headers {}, but received {}".format(
                first_headers, {*columns}
            ))
        raise AttributeError("Not valid core data headers, check log.")

    reactions = core_data.drop(first_headers, axis=1)
    shape = reactions.values.shape
    if shape[0] != shape[1]:
        logger.error(
            "The number of rows is different from the number of transcription "
            "factors -> {}".format(shape)
        )
        raise AttributeError("Not valid shape for core reactions, check log.")

    return core_data


def parse_y0_data(data: pd.DataFrame, filename: str, sep: str = "\t"
                  ) -> Vector:
    """
    Parse an input file containing the starting values for the core ODE system.

    :param data: The pandas.DataFrame to use as a reference for comparing the
        starting points.
    :param filename: Path to the file containing the y0 values.
    :param sep: Separator used in the file. Default is \t (tab).
    :return: Vector containing the y0 values.
    :raise AttributeError: if the number of elements in the file is not the same
        as the number of rows in the data.
    :raise OSError: If the file doesn't exist.
    """

    y0 = pd.read_csv(filename, sep=sep)

    if y0.shape[1] != data.shape[0]:
        logging.getLogger(__name__).error(
            "Number of columns in {} is different than number of transcription "
            "factors".format(filename)
        )
        raise AttributeError("Not valid number of starting values, check log.")
    return np.array(y0.values, dtype=Float).flatten()
