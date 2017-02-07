import logging
from configparser import ConfigParser, NoOptionError
from typing import List, Tuple, NamedTuple, Callable, Dict

from utilities.logger_setup import LoggerSetup

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

    def add_optional_key_value(self, key: str, value: str, *args: str
                               ) -> 'ConfigurationBuilder':
        commented_key = "#" + key
        comment = "Remove # in order to use the option."
        return self.add_key_value(commented_key, value, comment, *args)

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

    def parse_logger_section(self, section: str, setup: LoggerSetup):
        config = self.parse()._parser
        logger = logging.getLogger(__name__)
        log_file = None
        log_verbosity = False
        level = logging.WARNING
        for key in self.__expected[section]:
            try:
                verbosity = config.getboolean(section, key)
                log_verbosity = verbosity
            except ValueError:
                log_file = config.get(section, key, fallback=None)
            except NoOptionError:
                logger.info("Printing logs on terminal.")
        if log_verbosity:
            level = logging.INFO
            setup.change_root_level(level)
            setup.change_stream_level(level)
            logger.info("Logging in verbosity mode.")
        if log_file is not None:
            setup.set_file_log(log_file, level)
            logger.info(
                "Log file is {}".format(log_file)
            )

    def parse(self) -> 'ConfigurationParser':
        self._parser.read(self._filename)
        expected_sections = self.__expected.keys()
        if not set(expected_sections).issubset(self._parser.sections()):
            raise RuntimeError
        return self


def from_parser_to_builder(parser: ConfigurationParser):
    builder = ConfigurationBuilder(parser._filename)
    builder._parser = parser._parser
    return builder
