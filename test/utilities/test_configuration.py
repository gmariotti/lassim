import os
import re
from unittest import TestCase

from nose.tools import assert_equal

from utilities.configuration import ConfigurationBuilder, ConfigurationParser, \
    from_parser_to_builder
from utilities.data_classes import InputFiles

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class TestConfiguration(TestCase):
    def setUp(self):
        self.filename = "test_configuration.ini"
        self.network = "test_network.txt"
        self.data = ["test_data1.txt", "test_data2.txt"]
        self.time = "test_time.txt"
        self.perturbations = "commented option"
        self.optimization = "DE"
        self.opt_args = "opt.json"

        self.regex = re.compile(r'(?=\n)(\s+)')

    def tearDown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_CreateValidSingleSection(self):
        input_single_section = """[Input Data]
        network = test_network.txt
        ; data must be a list of values
        data = test_data1.txt, test_data2.txt
        ; first line of comment
        ; second line of comment
        times = test_time.txt
        ; remove # in order to use the option.
        #perturbations = commented option\n

        """
        expected = self.regex.sub(r'\n', input_single_section)

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
            actual = self.regex.sub(r'\n', config.read())
            assert_equal(expected, actual,
                         "\n\nExpected\n\n{}\n\nbut received\n\n{}".format(
                             expected, actual
                         ))

    def test_CreateValidMultipleSections(self):
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
        expected = self.regex.sub(r'\n', input_multiple_sections)

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
            actual = self.regex.sub(r'\n', config.read())
            assert_equal(expected, actual,
                         "\n\nExpected\n\n{}\n\nbut received\n\n{}".format(
                             expected, actual
                         ))

    def test_ReadValidSingleSectionWithComments(self):
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
        input_regex = self.regex.sub(r'\n', input_single_section)

        with open(self.filename, "w") as config_file:
            config_file.write(input_regex)
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
        # comments are removed from the configuration, but I don't know why

        input_single_section = """[Input Data]
        network = test_network{}.txt
        data = test_data1.txt, test_data2.txt
        times = test_time.txt

        """

        with open(self.filename, "w") as config_file:
            config_file.write(
                self.regex.sub(r'\n', input_single_section.format("")))

        parser = ConfigurationParser(
            self.filename
        ).define_section(
            "Input Data", "network", "data", "times", "perturbations"
        ).parse()

        builder = from_parser_to_builder(parser).add_section(
            "Input Data"
        ).add_key_value("network", "test_network2.txt")
        builder.build()

        expected = self.regex.sub(r'\n', input_single_section.format(2))

        with open(self.filename) as config_file:
            actual = self.regex.sub(r'\n', config_file.read())
            assert_equal(expected, actual,
                         "\n\nExpected\n\n{}\n\nbut received\n\n{}".format(
                             expected, actual
                         ))
