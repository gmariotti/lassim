import os
import shutil
from collections import namedtuple
from unittest import TestCase

import numpy as np
from nose.tools import assert_true

from core.handlers.serializers.plot_serializer import PlotSerializer

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class TestPlotSerializer(TestCase):
    def setUp(self):
        def filename_creator(d, l_n, s):
            for name in l_n:
                yield "{}/{}.png".format(d, name)

        def fake_results(sol):
            for _ in range(0, 2):
                yield np.zeros(2), np.ones(2), np.empty(2)

        self.dir_plots = ".test_dir_plots"
        if not os.path.isdir(self.dir_plots):
            os.makedirs(self.dir_plots)
        self.names = ["fig1", "fig2"]
        self.axis = [("a", "b"), ("a", "b")]
        self.serializer = PlotSerializer.new_instance(
            self.dir_plots, self.names, self.axis,
            fake_results, filename_creator
        )

    def tearDown(self):
        if os.path.isdir(self.dir_plots):
            shutil.rmtree(self.dir_plots)

    def test_SerializeSolution(self):
        fake_solution = namedtuple("Solution", ["x"])(0)
        self.serializer.serialize_solution(fake_solution)
        for name in self.names:
            expected_file = self.dir_plots + "/" + name + ".png"
            assert_true(os.path.isfile(expected_file),
                        "Expected file {} but not found".format(expected_file))
