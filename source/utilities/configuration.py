from configparser import ConfigParser
from copy import deepcopy
from typing import Iterable, Dict, List, Tuple

from utilities.data_classes import InputFiles

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class ConfigurationBuilder:
    __data_section = "Input Data"
    # FIXME - so stupid!
    __data_dict = {
        "network": False,
        "data": False,
        "times": False,
        "perturbations": False
    }

    def __init__(self, filename: str, allow_comments: bool = True):
        self.__filename = filename
        self.__parser = ConfigParser(allow_no_value=allow_comments)
        self.__expected = dict()

    def add_network(self, filename: str, *args: str) -> 'ConfigurationBuilder':
        self.__check_section(self.__data_section)
        self.__comment(args, self.__data_section)
        self.__parser.set(self.__data_section, "network", filename)
        return self

    def expect_network(self) -> 'ConfigurationBuilder':
        self.__check_section(self.__data_section)
        data_expected = self.__expect_section(
            self.__data_section, self.__data_dict
        )
        data_expected["network"] = True
        return self

    def add_data(self, filenames: Iterable[str], *args: str
                 ) -> 'ConfigurationBuilder':
        self.__check_section(self.__data_section)
        self.__comment(args, self.__data_section)
        value = ", ".join(filenames)
        self.__parser.set(self.__data_section, "data", value)
        return self

    def expect_data(self) -> 'ConfigurationBuilder':
        self.__check_section(self.__data_section)
        data_expected = self.__expect_section(
            self.__data_section, self.__data_dict
        )
        data_expected["data"] = True
        return self

    def add_time(self, filename: str, *args: str) -> 'ConfigurationBuilder':
        self.__check_section(self.__data_section)
        self.__comment(args, self.__data_section)
        self.__parser.set(self.__data_section, "times", filename)
        return self

    def expect_time(self) -> 'ConfigurationBuilder':
        self.__check_section(self.__data_section)
        data_expected = self.__expect_section(
            self.__data_section, self.__data_dict
        )
        data_expected["times"] = True
        return self

    def build(self):
        with open(self.__filename, "w") as config_file:
            self.__parser.write(config_file)

    def parse(self) -> 'ConfigurationBuilder':
        self.__parser.read(self.__filename)
        expected_sections = self.__expected.keys()
        if not set(expected_sections).issubset(self.__parser.sections()):
            raise RuntimeError
        return self

    def parse_input_data(self):
        parser = self.parse()
        expected_data = self.__expected[self.__data_section]
        arguments = {}
        for key, value in expected_data.items():
            if value:
                values = parser.__parser[self.__data_section][key].split(", ")
                if len(values) > 1:
                    arguments[key] = values
                else:
                    arguments[key] = values[0]
            else:
                arguments[key] = None
        return InputFiles(**arguments)

    def __check_section(self, section: str):
        # FIXME - change to annotation
        if not self.__parser.has_section(section):
            self.__parser.add_section(section)

    def __expect_section(self, section: str, expected: Dict) -> Dict:
        # FIXME - change to annotation
        section_data = self.__expected.setdefault(
            section, deepcopy(expected)
        )
        return section_data

    def __comment(self, comments: Tuple[str, ...], section: str):
        for comment in comments:
            if comment:
                self.__parser.set(section, "; " + comment)
