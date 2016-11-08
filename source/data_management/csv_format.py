import logging

import numpy as np
import pandas as pd
from sortedcontainers import SortedSet, SortedDict

from utilities.type_aliases import Float, Vector

"""
The parsers are used for tabular separated files.

The file with the list of transcription factors, must contain the headers
'source' for the name of the transcription factor and 'target' for the name of
the transcription factor on which has influence.

The patient data must be a tabular file with the following headers
["source", "t0", "t1", ..., "tn"]

The time sequence must be a tabular file with the following headers
["t0", "t1", ..., "tn"]

The perturbations files must be a tabular file with the following headers
["<source1>, ..., "<source_n>", "t_start", "t_end"]
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


def parse_network(filename: str, sep: str = "\t") -> SortedDict:
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


def parse_network_data(filename: str, sep: str = "\t",
                       d_type: np.dtype = Float) -> SortedDict:
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

    data_dictionary = SortedDict(
        {value[h_source]: np.array(value.drop([h_source]).values, dtype=d_type)
         for (i, value) in data.iterrows()
         }
    )

    return data_dictionary


def parse_time_sequence(filename: str, sep: str = "\t",
                        d_type: np.dtype = Float) -> Vector:
    times = pd.read_csv(filename, sep=sep)
    # check validity of headers
    columns = len(times.columns)
    valid_headers = set(["t{}".format(i) for i in range(0, columns)])
    if not valid_headers.issubset(times.columns):
        logging.getLogger(__name__).error(
            "Expected headers for time series are {}".format(valid_headers)
        )
        raise AttributeError("Not valid time series headers, check log.")

    return np.array(times.values, dtype=d_type).flatten()


def parse_perturbations_data(filename: str, sep: str = "\t") -> Vector:
    perturbations = pd.read_csv(filename, sep=sep)

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

    return perturbations.values
