from unittest import TestCase

import numpy as np
from nose.tools import assert_equal, assert_raises
from sortedcontainers import SortedDict

from core.core_problem import CoreProblemFactory
from core.factories import OptimizationFactory
from core.optimizations.basin_hopping import BHOptimization

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class TestOptimizationFactory(TestCase):
    def setUp(self):
        self.factory = CoreProblemFactory.new_instance(
            (np.ones(1), np.ones(1), np.ones(1)), np.ones(1), None)
        self.problem = self.factory.build(
            1, ([0], [1]), (np.ones(1), np.array([True]))
        )

    def test_NotValidOptimizationType(self):
        assert_raises(ReferenceError,
                      OptimizationFactory.new_optimization_instance,
                      "not-valid-type", self.factory,
                      (self.problem, SortedDict()), 0, None)

    def test_ValidShortOptimizationType(self):
        expected = BHOptimization.type_name
        actual = OptimizationFactory.get_optimization_type("BH")
        assert_equal(expected, actual,
                     "Expected {} but received {}".format(
                         expected, actual
                     ))

    def test_NotValidShortOptimizationType(self):
        assert_raises(ReferenceError,
                      OptimizationFactory.get_optimization_type,
                      "not-valid")
