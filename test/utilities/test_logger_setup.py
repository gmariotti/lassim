import logging
import os
from unittest import TestCase

from utilities.logger_setup import LoggerSetup

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class TestMySetup(TestCase):
    def setUp(self):
        self.logfile = "test.log"
        if os.path.isfile(self.logfile):
            os.remove(self.logfile)

    def tearDown(self):
        if os.path.isfile(self.logfile):
            os.remove(self.logfile)

    def test_LoggerWithFileLog(self):
        setup = LoggerSetup()
        setup.set_file_log(level=logging.INFO, logfile=self.logfile)
        log_message = "log test"
        logger = logging.getLogger(__name__)
        logger.info(log_message)
        expected = [log_message, "INFO"]

        with open(self.logfile) as logfile:
            # first two lines contains the change in level of the logger
            line = logfile.readline()
            line = logfile.readline()
            line = logfile.readline()
            for message in expected:
                self.assertIn(message, line,
                              "{} not found in line {}".format(message, line))
