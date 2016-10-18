from unittest import TestCase

import numpy as np
from nose.tools import assert_dict_equal, assert_tuple_equal
from numpy.testing import assert_array_equal
from sortedcontainers import SortedDict, SortedSet

from customs.core_functions import generate_reactions_vector, \
    remove_lowest_reaction, default_bounds

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class TestCustomFormatterFunctions(TestCase):
    def setUp(self):
        self.fake_network = SortedDict({
            "IRF4": SortedSet(["NFATC3"]),
            "MAF": SortedSet(["IRF4", "NFATC3", "STAT3"]),
            "NFATC3": SortedSet(),
            "STAT3": SortedSet(["IRF4"])
        })
        # this fake reactions are the same that would have been obtained from
        # creating a CoreSystem object from the fake network
        self.fake_reactions = SortedDict({
            0: SortedSet([2]),
            1: SortedSet([0, 2, 3]),
            2: SortedSet([0, 1, 2, 3]),
            3: SortedSet([0])
        })

    def test_DefaultBounds(self):
        expected = ([0.0, 0.0, 0.0, 0.0, -20.0, -20.0],
                    [20.0, 20.0, 20.0, 20.0, 20.0, 20.0])
        actual = default_bounds(2, 2)
        assert_tuple_equal(expected, actual,
                           "Expected {}\nbut actual {}".format(
                               expected, actual
                           ))

    def test_GenerateReactionsVector(self):
        exp_reactions = np.array([0, 0, -1, 0,
                                  -1, 0, -1, -1,
                                  -1, -1, -1, -1,
                                  -1, 0, 0, 0], dtype=np.float32)
        exp_mask = np.array([False, False, True, False,
                             True, False, True, True,
                             True, True, True, True,
                             True, False, False, False])
        act_reactions, act_mask = generate_reactions_vector(self.fake_reactions)
        assert_array_equal(exp_reactions, act_reactions,
                           "Expected\n{}\nbut actual\n{}".format(
                               exp_reactions, act_reactions
                           ))
        assert_array_equal(exp_mask, act_mask,
                           "Expected\n{}\nbut actual\n{}".format(
                               exp_mask, act_mask
                           ))

    def test_RemoveLowestReaction(self):
        fake_result = np.array([0, 0, 0, 0,
                                0, 0, 0, 0,
                                -1, 2, 3, -4, 1, 0.5, 6, 0.5, -11])
        exp_result = np.array([0, 0, 0, 0,
                               0, 0, 0, 0,
                               -1, 2, 3, -4, 1, 6, 0.5, -11])
        exp_reactions = SortedDict({
            0: SortedSet([2]),
            1: SortedSet([0, 2, 3]),
            2: SortedSet([0, 2, 3]),
            3: SortedSet([0])
        })
        act_result, act_reactions = remove_lowest_reaction(
            fake_result, self.fake_reactions
        )
        assert_array_equal(exp_result, act_result,
                           "Expected\n{}\nbut actual\n{}".format(
                               exp_result, act_result
                           ))
        assert_dict_equal(exp_reactions, act_reactions,
                          "Expected\n{}\nbut actual\n{}".format(
                              exp_reactions, act_reactions
                          ))

    def test_IterationFunctionWithMaskAllFalse(self):
        self.fail()

    def test_IterationFunctionWithMaskOneTrue(self):
        self.fail()

    def test_IterationFunctionWithMaskUnlTrue(self):
        self.fail()
