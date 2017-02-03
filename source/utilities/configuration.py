from configparser import ConfigParser
from typing import List, Tuple, NamedTuple, Callable, Dict

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class Configuration:
    def __init__(self, filename: str, allow_comments: bool = True):
        self._filename = filename
        self._parser = ConfigParser(allow_no_value=allow_comments)

    def _check_section(self, section: str):
        # FIXME - change to annotation
        if not self._parser.has_section(section):
            self._parser.add_section(section)

    def _comment(self, comments: Tuple[str, ...], section: str):
        for comment in comments:
            if comment:
                self._parser.set(section, "; " + comment)


class ConfigurationBuilder(Configuration):
    def __init__(self, filename: str, allow_comments: bool = True):
        super(ConfigurationBuilder, self).__init__(filename, allow_comments)
        self.__current_section = "DEFAULT"

    def add_section(self, section: str, *args: str) -> 'ConfigurationBuilder':
        self._check_section(section)
        self._comment(args, section)
        self.__current_section = section
        return self

    def add_key_value(self, key: str, value: str, *args: str
                      ) -> 'ConfigurationBuilder':
        self._comment(args, self.__current_section)
        self._parser.set(self.__current_section, key, value)
        return self

    def add_key_values(self, key: str, values: List[str], *args: str
                       ) -> 'ConfigurationBuilder':
        self._comment(args, self.__current_section)
        value = ", ".join(values)
        self._parser.set(self.__current_section, key, value)
        return self

    def build(self):
        with open(self._filename, "w") as config_file:
            self._parser.write(config_file)


class ConfigurationParser(Configuration):
    def __init__(self, filename: str, allow_comments: bool = True):
        super(ConfigurationParser, self).__init__(filename, allow_comments)
        self.__expected = {}

    def define_section(self, section: str, *args: str) -> 'ConfigurationParser':
        self.__expected.setdefault(section, [key for key in args])
        return self

    def parse_section(self, section: str, dataclass: NamedTuple,
                      conversion: Callable[[Dict], Dict] = None) -> NamedTuple:
        parsed_section = self.parse()._parser[section]
        expected_keys = self.__expected[section]
        arguments = {}
        for key in expected_keys:
            try:
                values = parsed_section[key].split(", ")
                if len(values) > 1:
                    arguments[key] = values
                else:
                    arguments[key] = values[0]
            except KeyError:
                arguments[key] = None
        if conversion is not None:
            arguments = conversion(arguments)
        return dataclass(**arguments)

    def parse(self) -> 'ConfigurationParser':
        self._parser.read(self._filename)
        expected_sections = self.__expected.keys()
        if not set(expected_sections).issubset(self._parser.sections()):
            raise RuntimeError
        return self
