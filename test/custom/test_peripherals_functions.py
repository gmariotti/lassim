from unittest import TestCase

import numpy as np
from nose.tools import assert_dict_equal
from numpy.testing import assert_array_equal
from sortedcontainers import SortedDict, SortedSet

from customs.peripherals_functions import generate_core_vector, \
    remove_lowest_reaction, generate_reactions_vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class TestPeripheralsFunctions(TestCase):
    def setUp(self):
        self.assert_message = "expected\n{}\nbut actual\n{}"

    def test_RemoveLowestReactionMultipleGenes(self):
        # number from 0 to 10 - first 6 values are lambdas and vmax
        solution_vector = np.arange(11)
        reactions = SortedDict({
            11: SortedSet([1, 2]),
            44: SortedSet([1, 4, 5]),
            55: SortedSet()
        })
        expected_vector = np.array([
            0, 1, 2, 3, 4, 5,  # lambdas + vmax
            7, 8, 9, 10  # reactions
        ])
        expected_reactions = SortedDict({
            11: SortedSet([2]),
            44: SortedSet([1, 4, 5]),
            55: SortedSet()
        })
        actual_vector, actual_reactions = remove_lowest_reaction(
            solution_vector, reactions
        )
        assert_array_equal(expected_vector, actual_vector,
                           self.assert_message.format(
                               expected_vector, actual_vector
                           ))
        assert_dict_equal(expected_reactions, actual_reactions,
                          self.assert_message.format(
                              expected_reactions, actual_reactions
                          ))

    def test_RemoveLowestReactionSingleGeneMiddle(self):
        solution_vector = np.array([
            1, 10,  # lambdas and vmax
            10, -2, 20, 16  # reactions
        ])
        reactions = SortedDict({
            44: SortedSet([1, 4, 5, 10])
        })
        expected_vector = np.array([
            1, 10,  # lambdas + vmax
            10, 20, 16  # reactions
        ])
        expected_reactions = SortedDict({
            44: SortedSet([1, 5, 10])
        })
        actual_vector, actual_reactions = remove_lowest_reaction(
            solution_vector, reactions
        )
        assert_array_equal(expected_vector, actual_vector,
                           self.assert_message.format(
                               expected_vector, actual_vector
                           ))
        assert_dict_equal(expected_reactions, actual_reactions,
                          self.assert_message.format(
                              expected_reactions, actual_reactions
                          ))

    def test_RemoveLowestReactionSingleGeneLast(self):
        solution_vector = np.array([
            1, 10,  # lambdas and vmax
            10, 11, -10, -5  # reactions
        ])
        reactions = SortedDict({
            44: SortedSet([1, 4, 5, 12])
        })
        expected_vector = np.array([
            1, 10,  # lambdas + vmax
            10, 11, -10  # reactions
        ])
        expected_reactions = SortedDict({
            44: SortedSet([1, 4, 5])
        })
        actual_vector, actual_reactions = remove_lowest_reaction(
            solution_vector, reactions
        )
        assert_array_equal(expected_vector, actual_vector,
                           self.assert_message.format(
                               expected_vector, actual_vector
                           ))
        assert_dict_equal(expected_reactions, actual_reactions,
                          self.assert_message.format(
                              expected_reactions, actual_reactions
                          ))

    def test_GenerateCoreVectorMultipleGenes(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        num_tf = 3
        num_react = 5
        gene_reactions = SortedDict({
            10: SortedSet([0, 1]),
            12: SortedSet([0, 1, 2]),
            44: SortedSet()
        })
        expected_core = np.array([
            1, 1, 1, np.inf, np.inf, np.inf,  # lambdas
            10, 10, 10, np.inf, np.inf, np.inf,  # vmax
            2, 2, 2, -2, -2,  # core reactions
            np.inf, np.inf,  # gene 10 reactions
            np.inf, np.inf, np.inf  # gene 12 reaction
        ])
        expected_mask = np.array([
            False, False, False, True, True, True,  # lambdas
            False, False, False, True, True, True,  # vmax
            False, False, False, False, False,  # core reactions
            True, True,  # gene 10 reactions
            True, True, True  # gene 12 reactions
        ])
        actual_core, actual_mask = generate_core_vector(
            core_data, num_tf, num_react, gene_reactions
        )
        assert_array_equal(expected_core, actual_core,
                           self.assert_message.format(
                               expected_core, actual_core
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))

    def test_GenerateCoreVectorSingleGeneFull(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        num_tf = 3
        num_react = 5
        gene_reactions = SortedDict({
            12: SortedSet([0, 1, 2])
        })
        expected_core = np.array([
            1, 1, 1, np.inf,  # lambdas
            10, 10, 10, np.inf,  # vmax
            2, 2, 2, -2, -2,  # core reactions
            np.inf, np.inf, np.inf  # gene 12 reaction
        ])
        expected_mask = np.array([
            False, False, False, True,  # lambdas
            False, False, False, True,  # vmax
            False, False, False, False, False,  # core reactions
            True, True, True  # gene 12 reactions
        ])
        actual_core, actual_mask = generate_core_vector(
            core_data, num_tf, num_react, gene_reactions
        )
        assert_array_equal(expected_core, actual_core,
                           self.assert_message.format(
                               expected_core, actual_core
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))

    def test_GenerateCoreVectorSingleGeneEmpty(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        num_tf = 3
        num_react = 5
        gene_reactions = SortedDict({
            44: SortedSet()
        })
        expected_core = np.array([
            1, 1, 1, np.inf,  # lambdas
            10, 10, 10, np.inf,  # vmax
            2, 2, 2, -2, -2  # core reactions
        ])
        expected_mask = np.array([
            False, False, False, True,  # lambdas
            False, False, False, True,  # vmax
            False, False, False, False, False  # core reactions
        ])
        actual_core, actual_mask = generate_core_vector(
            core_data, num_tf, num_react, gene_reactions
        )
        assert_array_equal(expected_core, actual_core,
                           self.assert_message.format(
                               expected_core, actual_core
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))

    def test_GenerateCoreVectorSingleGeneNotFull(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        num_tf = 3
        num_react = 5
        gene_reactions = SortedDict({
            10: SortedSet([0, 1])
        })
        expected_core = np.array([
            1, 1, 1, np.inf,  # lambdas
            10, 10, 10, np.inf,  # vmax
            2, 2, 2, -2, -2,  # core reactions
            np.inf, np.inf  # gene 10 reactions
        ])
        expected_mask = np.array([
            False, False, False, True,  # lambdas
            False, False, False, True,  # vmax
            False, False, False, False, False,  # core reactions
            True, True  # gene 10 reactions
        ])
        actual_core, actual_mask = generate_core_vector(
            core_data, num_tf, num_react, gene_reactions
        )
        assert_array_equal(expected_core, actual_core,
                           self.assert_message.format(
                               expected_core, actual_core
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))

    def test_GenerateReactionsVectorMultipleGenes(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        gene_reactions = SortedDict({
            10: SortedSet([0, 1]),
            12: SortedSet([0, 1, 2]),
            44: SortedSet()
        })
        expected_vector = np.array([
            2, 2, 2, 0, 0, 0, -2, 0, -2,  # reactions of the core
            np.inf, np.inf, 0,  # reactions gene 10
            np.inf, np.inf, np.inf,  # reactions gene 12
            0, 0, 0  # reactions gene 44
        ])
        expected_mask = np.array([
            False, False, False, False, False, False, False, False, False,
            True, True, False,
            True, True, True,
            False, False, False,
        ])
        actual_vector, actual_mask = generate_reactions_vector(
            gene_reactions, core_data
        )
        assert_array_equal(expected_vector, actual_vector,
                           self.assert_message.format(
                               expected_vector, actual_vector
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))

    def test_GenerateReactionsVectorSingleGeneNoReactions(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        gene_reactions = SortedDict({
            44: SortedSet()
        })
        expected_vector = np.array([
            2, 2, 2, 0, 0, 0, -2, 0, -2,  # reactions of the core
            0, 0, 0  # reactions gene 44
        ])
        expected_mask = np.array([
            False, False, False, False, False, False, False, False, False,
            False, False, False,
        ])
        actual_vector, actual_mask = generate_reactions_vector(
            gene_reactions, core_data
        )
        assert_array_equal(expected_vector, actual_vector,
                           self.assert_message.format(
                               expected_vector, actual_vector
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))

    def test_GenerateReactionsVectorSingleGene1Reaction(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        gene_reactions = SortedDict({
            10: SortedSet([0])
        })
        expected_vector = np.array([
            2, 2, 2, 0, 0, 0, -2, 0, -2,  # reactions of the core
            np.inf, 0, 0  # reactions gene 10
        ])
        expected_mask = np.array([
            False, False, False, False, False, False, False, False, False,
            True, False, False
        ])
        actual_vector, actual_mask = generate_reactions_vector(
            gene_reactions, core_data
        )
        assert_array_equal(expected_vector, actual_vector,
                           self.assert_message.format(
                               expected_vector, actual_vector
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))

    def test_GenerateReactionsVectorSingleGeneAllReactions(self):
        # represents the data of a core. First value of each list is the lambda,
        # the second is the vmax and the rest of them are the reactions
        core_data = np.array([
            [1, 10, 2, 2, 2], [1, 10, 0, 0, 0], [1, 10, -2, 0, -2]
        ])
        gene_reactions = SortedDict({
            12: SortedSet([0, 1, 2])
        })
        expected_vector = np.array([
            2, 2, 2, 0, 0, 0, -2, 0, -2,  # reactions of the core
            np.inf, np.inf, np.inf  # reactions gene 12
        ])
        expected_mask = np.array([
            False, False, False, False, False, False, False, False, False,
            True, True, True
        ])
        actual_vector, actual_mask = generate_reactions_vector(
            gene_reactions, core_data
        )
        assert_array_equal(expected_vector, actual_vector,
                           self.assert_message.format(
                               expected_vector, actual_vector
                           ))
        assert_array_equal(expected_mask, actual_mask,
                           self.assert_message.format(
                               expected_mask, actual_mask
                           ))
