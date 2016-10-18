import csv
import errno
import os

import numpy as np
from sortedcontainers import SortedSet, SortedDict

"""
The parsers are used for tabular separated files.

The file with the list of transcription factors, must contain the headers
'source' for the name of the transcription factor and 'target' for the name of
the transcription factor on which has influence.

The patient data must be a tabular file with the following headers
["source", "t0", "t1", ..., "tn"]

The time sequence must be a tabular file with the following headers
["t0", "t1", ..., "tn"]
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


def open_file(func):
    def wrapper(filename):
        if os.path.isfile(filename):
            with open(filename) as file_to_read:
                return func(file_to_read)
        else:
            # TODO - logging
            print("{} not found.".format(filename))
            exit(errno.ENOENT)

    return wrapper


@open_file
def parse_network(filename):
    reader = csv.DictReader(filename, delimiter="\t")
    network = SortedDict()
    for row in reader:
        target = row["target"]
        tfact = row["source"]
        if tfact not in network.keys():
            network[tfact] = SortedSet()
        network[tfact].add(target)

    return network


@open_file
def parse_patient_data(filename, dtype=np.float64):
    reader = csv.DictReader(filename, delimiter="\t")
    data_dictionary = SortedDict()
    # TODO - check validity
    # what it should do is to remove just the TF field and order the other
    # based on the fact that the list is t0 to tn
    fields = reader.fieldnames.copy()
    fields.remove("source")
    time_headers = SortedSet(fields)
    for row in reader:
        tfact = row["source"]
        data_dictionary[tfact] = np.array([row[head] for head in time_headers],
                                          dtype=dtype)
    return data_dictionary


@open_file
def parse_time_sequence(filename, dtype=np.uint32):
    reader = csv.DictReader(filename, delimiter="\t")
    # TODO - check validity
    time_headers = SortedSet(reader.fieldnames)
    return np.array([row[header] for row in reader
                     for header in time_headers],
                    dtype=dtype)
