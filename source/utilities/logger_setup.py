import logging
import os

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class LoggerSetup:
    """
    This class is used for the setup of the root logger.
    """

    def __init__(self, level=logging.WARNING):
        self._logfile = None
        self._file_handler = None

        # get the root logger
        logger = logging.getLogger()
        # example = 2016/08/29 [WARNING] - 10:05:29AM
        self._formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] - %(message)s",
            datefmt="%Y/%m/%d %I:%M:%S%p"
        )
        # init the streamhandler
        # StreamHandler default is sys.stderr
        self._stream_handler = logging.StreamHandler()
        self._stream_handler.setLevel(level)
        self._stream_handler.setFormatter(self._formatter)
        logger.addHandler(self._stream_handler)

    def set_file_log(self, logfile, level=logging.WARNING):
        logger = logging.getLogger()

        # check that the directory where to put the logfile exist
        directory = os.path.dirname(logfile)
        # checks also that the name of the directory is not an empty string
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)

        self._file_handler = logging.FileHandler(logfile)
        self._file_handler.setLevel(level)
        self._file_handler.setFormatter(self._formatter)
        self._logfile = logfile
        logger.addHandler(self._file_handler)
        logger.info("Level for file set to {}".format(
            logging.getLevelName(level)
        ))
        # if a log file is present, sys.stderr prints only WARNING or more
        self.change_stream_level(logging.WARNING)

    def change_root_level(self, level):
        logger = logging.getLogger()
        logger.setLevel(level)
        logger.info("Root logger level changed to {}".format(
            logging.getLevelName(level)
        ))

    def change_stream_level(self, level):
        self._stream_handler.setLevel(level)
        logging.getLogger().info("Level for stderr set to {}".format(
            logging.getLevelName(level)
        ))
