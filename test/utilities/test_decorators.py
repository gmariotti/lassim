import os
from unittest import TestCase

from data_management.csv_format import open_file

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class TestDecorators(TestCase):
    def setUp(self):
        self.temp = "temp-file"
        self.test_text = "This is a test line just to see if is read or not"
        if not os.path.exists(self.temp):
            with open(self.temp, "w") as file_:
                file_.write(self.test_text)

    def tearDown(self):
        if os.path.exists(self.temp):
            os.remove(self.temp)

    def test_OpenFileDecorator(self):
        @open_file
        def test_func(filename):
            line = filename.readline()
            return line

        actual = test_func(self.temp)
        self.assertEqual(self.test_text, actual,
                         "Error, expected\n{}\nreceived\n{}".format(
                             self.test_text, actual
                         ))
