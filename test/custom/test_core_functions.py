from collections import namedtuple
from unittest import TestCase

import numpy as np
from PyGMO.core import champion
from nose.tools import assert_dict_equal, assert_tuple_equal, assert_false, \
    assert_true
from numpy.testing import assert_array_equal
from sortedcontainers import SortedDict, SortedSet

from core.core_problem import CoreProblemFactory
from core.functions.common_functions import odeint1e8_lassim
from core.functions.perturbation_functions import perturbation_func_sequential
from core.solutions.lassim_solution import LassimSolution
from customs.core_functions import generate_reactions_vector, \
    remove_lowest_reaction, default_bounds, iter_function

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class TestCoreFunctions(TestCase):
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

        data = np.reshape(np.linspace(0, 100, num=100), (10, 10))
        pert_data = data.copy()
        sigma = np.linspace(0, 1, num=10)
        times = np.linspace(0, 100, num=10)
        y0 = np.linspace(0, 100, num=10)

        self.factory = CoreProblemFactory.new_instance(
            (data, sigma, times, pert_data), y0, odeint1e8_lassim,
            perturbation_func_sequential
        )
        self.fake_champion = champion()
        # 17 = 4lambdas + 4vmax + 9reactions
        self.fake_champion.x = np.linspace(0, 10, num=17)
        self.fake_champion.f = (0.99,)
        # too lazy to create an entire CoreProblem
        self.FakeProblem = namedtuple("FakeProblem",
                                      ["vector_map", "vector_map_mask"])

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

    # the mask used in the test_IterationFunction* doesn't really make sense.
    # What is important here, is that the function returns true or false
    # based on what is in the mask
    def test_IterationFunctionWithMaskAllFalse(self):
        solution = LassimSolution(
            self.fake_champion, self.fake_reactions,
            self.FakeProblem(np.linspace(0, 10, 9),
                             np.array([False for _ in range(0, 9)]))
        )
        new_problem, new_reactions, iteration = iter_function(
            self.factory, solution
        )
        assert_false(iteration, "An iteration wasn't expected.")

    def test_IterationFunctionWithMaskOneTrue(self):
        mask = [False for _ in range(0, 8)]
        mask.append(True)
        solution = LassimSolution(
            self.fake_champion, self.fake_reactions,
            self.FakeProblem(np.linspace(0, 10, 9), np.array(mask))
        )
        new_problem, new_reactions, iteration = iter_function(
            self.factory, solution
        )
        assert_true(iteration, "An iteration was expected.")

    def test_IterationFunctionWithMaskUnlTrue(self):
        mask = [False for _ in range(0, 7)]
        mask.append(True)
        mask.append(True)
        solution = LassimSolution(
            self.fake_champion, self.fake_reactions,
            self.FakeProblem(np.linspace(0, 10, 9), np.array(mask))
        )
        for i in range(0, 9):
            new_problem, new_reactions, iteration = iter_function(
                self.factory, solution
            )
            assert_true(iteration, "Expected iteration at try {}".format(i))
            solution = LassimSolution(
                self.fake_champion, new_reactions, new_problem
            )
        new_problem, new_reactions, iteration = iter_function(
            self.factory, solution
        )
        assert_false(iteration, "No iteration expected at the end.")
