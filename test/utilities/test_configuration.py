import os
from unittest import TestCase

from nose.tools import assert_equal

from utilities.configuration import ConfigurationBuilder
from utilities.data_classes import InputFiles

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

input_config = """[Input Data]
network = test_network.txt
; data must be a list of values
data = test_data1.txt, test_data2.txt
; first line of comment
; second line of comment
times = test_time.txt

"""


class TestConfiguration(TestCase):
    def setUp(self):
        self.filename = "test_configuration.ini"
        self.network = "test_network.txt"
        self.data = ["test_data1.txt", "test_data2.txt"]
        self.time = "test_time.txt"

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_ValidInputData(self):
        ConfigurationBuilder(
            self.filename
        ).add_network(
            self.network
        ).add_data(
            self.data, "data must be a list of values"
        ).add_time(
            self.time, "first line of comment", "second line of comment"
        ).build()

        with open(self.filename) as config:
            actual = config.read()
            assert_equal(input_config, actual,
                         "\n\nExpected\n\n{}\n\nbut received\n\n{}".format(
                             input_config, actual
                         ))

    def test_ReadValidInputData(self):
        with open(self.filename, "w") as config_file:
            config_file.write(input_config)
        expected = InputFiles(self.network, self.data, self.time, None)

        actual = ConfigurationBuilder(
            self.filename
        ).expect_network(
        ).expect_data(
        ).expect_time(
        ).parse_input_data()

        assert_equal(expected, actual, "Expected {} but actual {}".format(
            expected, actual
        ))
