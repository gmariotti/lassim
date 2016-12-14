import os
from unittest import TestCase

import numpy as np
import pandas as pd
from nose.tools import assert_dict_equal, assert_list_equal, assert_set_equal, \
    assert_true
from numpy.testing import assert_array_equal
from pandas.util.testing import assert_frame_equal
from sortedcontainers import SortedDict, SortedSet

from data_management.csv_format import parse_time_sequence, parse_patient_data, \
    parse_network, parse_core_data, parse_peripherals_network

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

network_data = """source\ttarget
KLF6\tNFKB1
MYB\tNFKB1
MYB\tMYB
GATA3\tNFATC3"""

patient_file_data = """source\tt0\tt1\tt2
NFATC3\t0\t3\t100
GATA3\t0\t33\t99.9
NFKB1\t1\t3\t89"""

time_sequence_file_data = """t0\tt1\tt2\tt3
0\t1\t2\t3"""

complete_network_data = """source\ttf1\ttf2\ttf3
gene1\t1\t1\t1
gene2\t0\t1\t0
gene3\t0\t0\t0
gene4\tNaN\tNaN\t1
"""


class TestCSVFormat(TestCase):
    @classmethod
    def setUpClass(cls):
        # initialize network data file
        cls.network_filename = "test-network.csv"
        with open(cls.network_filename, "w") as networkfile:
            networkfile.write(network_data)

        # initialize patient data file
        cls.patient_filename = "test-datap.csv"
        with open(cls.patient_filename, "w") as patientdata:
            patientdata.write(patient_file_data)

        # initialize time sequence file
        cls.time_sequence_filename = "test-timeseq.csv"
        with open(cls.time_sequence_filename, "w") as timeseq:
            timeseq.write(time_sequence_file_data)

        cls.complete_network_filename = "test-complete_network.csv"
        with open(cls.complete_network_filename, "w") as networkfile:
            networkfile.write(complete_network_data)

        cls.core_data_filename = "test-core_data.csv"

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.network_filename):
            os.remove(cls.network_filename)

        if os.path.isfile(cls.patient_filename):
            os.remove(cls.patient_filename)

        if os.path.isfile(cls.time_sequence_filename):
            os.remove(cls.time_sequence_filename)

        if os.path.isfile(cls.complete_network_filename):
            os.remove(cls.complete_network_filename)

        if os.path.isfile(cls.core_data_filename):
            os.remove(cls.core_data_filename)

    def test_ParseNetwork(self):
        expected = SortedDict({
            "KLF6": SortedSet(["NFKB1"]),
            "MYB": SortedSet(["NFKB1", "MYB"]),
            "GATA3": SortedSet(["NFATC3"])
        })
        actual = parse_network(self.network_filename)
        assert_dict_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_ParsePatientData(self):
        data = np.array([
            np.array([0, 3, 100], dtype=np.float64),
            np.array([0, 33, 99.9], dtype=np.float64),
            np.array([1, 3, 89], dtype=np.float64)
        ])
        expected = pd.DataFrame(
            data=data, columns=["t0", "t1", "t2"],
            index=["NFATC3", "NFKB1", "GATA3"]
        )
        actual = parse_patient_data(self.patient_filename)
        assert_frame_equal(expected, actual,
                           "Expected\n{}\nreceived\n{}".format(
                               expected, actual
                           ))

    def test_ParseTimeSequence(self):
        expected = np.array([0, 1, 2, 3], dtype=np.uint32)
        actual = parse_time_sequence(self.time_sequence_filename)
        assert_true(np.array_equal(expected, actual),
                    "Expected\n{}\nreceived\n{}".format(expected, actual))

    def test_ParseCompleteNetwork(self):
        expected = SortedDict({
            "gene1": SortedSet(["tf1", "tf2", "tf3"]),
            "gene2": SortedSet(["tf2"]),
            "gene3": SortedSet(),
            "gene4": SortedSet(["tf1", "tf2", "tf3"])
        })
        actual = parse_peripherals_network(self.complete_network_filename)
        assert_dict_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_ParseCoreData(self):
        values = np.reshape(np.arange(15), (3, 5))
        dframe = pd.DataFrame(
            values, columns=["lambda", "vmax", "tf1", "tf2", "tf3"],
            dtype=np.float64
        )
        dframe.to_csv(self.core_data_filename, sep="\t", index=False)
        expected_values = np.array([
            [0.0, 1.0, 2.0, 3.0, 4.0],
            [5.0, 6.0, 7.0, 8.0, 9.0],
            [10.0, 11.0, 12.0, 13.0, 14.0]
        ], dtype=np.float64)
        expected_columns = ["lambda", "vmax", "tf1", "tf2", "tf3"]

        actual_dframe = parse_core_data(self.core_data_filename)
        assert_array_equal(expected_values, actual_dframe.values,
                           "Expected\n{}\nbut actual\n{}".format(
                               expected_values, actual_dframe.values
                           ))
        assert_list_equal(expected_columns, [*actual_dframe.columns],
                          "Expected\n{}\nbut actual\n{}".format(
                              expected_columns, actual_dframe.columns
                          ))
