import os
from unittest import TestCase

from nose.tools import assert_equal

from utilities.configuration import ConfigurationBuilder, ConfigurationParser
from utilities.data_classes import InputFiles

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

input_single_section = """[Input Data]
network = test_network.txt
; data must be a list of values
data = test_data1.txt, test_data2.txt
; first line of comment
; second line of comment
times = test_time.txt
; remove # in order to use the option.
#perturbations = commented option

"""

input_multiple_sections = """[Input Data]
network = test_network.txt
; data must be a list of values
data = test_data1.txt, test_data2.txt
; first line of comment
; second line of comment
times = test_time.txt

[Second section]
; extra arguments
optimization = DE
arguments long = opt.json

"""


class TestConfiguration(TestCase):
    def setUp(self):
        self.filename = "test_configuration.ini"
        self.network = "test_network.txt"
        self.data = ["test_data1.txt", "test_data2.txt"]
        self.time = "test_time.txt"
        self.perturbations = "commented option"
        self.optimization = "DE"
        self.opt_args = "opt.json"

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_CreateValidInputData(self):
        ConfigurationBuilder(
            self.filename
        ).add_section(
            "Input Data"
        ).add_key_value(
            "network", self.network
        ).add_key_values(
            "data", self.data, "data must be a list of values"
        ).add_key_value(
            "times", self.time,
            "first line of comment", "second line of comment"
        ).add_optional_key_value(
            "perturbations", self.perturbations
        ).build()

        with open(self.filename) as config:
            actual = config.read()
            assert_equal(input_single_section, actual,
                         "\n\nExpected\n\n{}\n\nbut received\n\n{}".format(
                             input_single_section, actual
                         ))

    def test_CreateValidMultipleSections(self):
        ConfigurationBuilder(
            self.filename
        ).add_section(
            "Input Data"
        ).add_key_value(
            "network", self.network
        ).add_key_values(
            "data", self.data, "data must be a list of values"
        ).add_key_value(
            "times", self.time,
            "first line of comment", "second line of comment"
        ).add_section(
            "Second section", "extra arguments"
        ).add_key_value(
            "optimization", self.optimization
        ).add_key_value(
            "arguments long", self.opt_args
        ).build()

        with open(self.filename) as config:
            actual = config.read()
            assert_equal(input_multiple_sections, actual,
                         "\n\nExpected\n\n{}\n\nbut received\n\n{}".format(
                             input_multiple_sections, actual
                         ))

    def test_ReadValidInputData(self):
        with open(self.filename, "w") as config_file:
            config_file.write(input_single_section)
        expected = InputFiles(self.network, self.data, self.time, None)

        actual = ConfigurationParser(
            self.filename
        ).define_section(
            "Input Data", "network", "data", "times", "perturbations"
        ).parse_section("Input Data", InputFiles)

        assert_equal(expected, actual, "Expected {} but actual {}".format(
            expected, actual
        ))

    def test_ReadModifyWriteConfiguration(self):
        # FIXME
        with open(self.filename, "w") as config_file:
            config_file.write(input_multiple_sections)

        # config = ConfigurationBandP(self.filename, read=True)
        self.fail()
