import os
from unittest import TestCase

import numpy as np
from sortedcontainers import SortedDict, SortedSet

from data_management.csv_format import parse_time_sequence, parse_network_data, \
    parse_network

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

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


class TestDataParsing(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.network_filename):
            os.remove(cls.network_filename)

        if os.path.isfile(cls.patient_filename):
            os.remove(cls.patient_filename)

        if os.path.isfile(cls.time_sequence_filename):
            os.remove(cls.time_sequence_filename)

    def test_ParseNetwork(self):
        expected = SortedDict({
            "KLF6": SortedSet(["NFKB1"]),
            "MYB": SortedSet(["NFKB1", "MYB"]),
            "GATA3": SortedSet(["NFATC3"])
        })
        actual = parse_network(self.network_filename)
        self.assertDictEqual(expected, actual,
                             "Expected\n{}\nbut actual\n{}".format(
                                 expected, actual
                             ))

    def test_ParsePatientData(self):
        expected = SortedDict({
            "NFATC3": np.array([0, 3, 100], dtype=np.float64),
            "GATA3": np.array([0, 33, 99.9], dtype=np.float64),
            "NFKB1": np.array([1, 3, 89], dtype=np.float64)
        })
        actual = parse_network_data(self.patient_filename)
        # can't use assertDictEqual because of numpy array
        self.assertSetEqual(set(expected.keys()), set(actual.keys()),
                            "Expected\n{}\nreceived\n{}".format(
                                expected.keys(),
                                actual.keys())
                            )
        for key, value in expected.items():
            self.assertTrue(np.array_equal(value, actual[key]),
                            "Expected\n{}\nreceived\n{}".format(value,
                                                                actual[key]))

    def test_ParseTimeSequence(self):
        expected = np.array([0, 1, 2, 3], dtype=np.uint32)
        actual = parse_time_sequence(self.time_sequence_filename)
        self.assertTrue(np.array_equal(expected, actual),
                        "Expected\n{}\nreceived\n{}".format(expected, actual))
