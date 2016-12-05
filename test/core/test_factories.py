from unittest import TestCase

import numpy as np
from nose.tools import assert_raises

from core.factories import OptimizationFactory
from core.problems.core_problem import CoreProblemFactory

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.2.0"


class TestOptimizationFactory(TestCase):
    def setUp(self):
        self.factory = CoreProblemFactory.new_instance(
            (np.ones(1), np.ones(1), np.ones(1)), np.ones(1), None
        )
        self.problem = self.factory.build(
            1, ([0], [1]), (np.ones(1), np.array([True]))
        )

    def test_NotValidBaseOptimization(self):
        assert_raises(KeyError,
                      OptimizationFactory.new_base_optimization,
                      "not-valid-type", None)
