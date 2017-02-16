from collections import namedtuple
from unittest import TestCase

import numpy as np
import pandas as pd
import pandas.util.testing as pdt
from PyGMO.core import champion
from nose.tools import assert_equal, assert_raises, assert_not_equal
from sortedcontainers import SortedDict, SortedSet

from core.solutions.peripheral_solution import PeripheralSolution

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def create_fake_solution(cost: float) -> PeripheralSolution:
    # first six values are lambdas and vmax
    fake_champion = champion()
    fake_champion.x = (1, 1.5, 10, 21)
    fake_champion.f = (cost,)
    fake_champion.c = ()
    fake_reactions = SortedDict({
        44: SortedSet([0, 2])
    })
    fake_k_react = (
        np.array([10, 15, 1, 0, 11, 0, 0, 11, 1,
                  1, 0, 1], dtype=np.float64),
        np.array([True, True, True, False, True, False, False, True, True,
                  True, False, True])
    )
    # too lazy to create an entire NetworkProblem
    FakeProblem = namedtuple("FakeProblem", ["vector_map", "vector_map_mask"])

    return PeripheralSolution(
        fake_champion, fake_reactions,
        FakeProblem(fake_k_react[0], fake_k_react[1])
    )


class TestPeripheralSolution(TestCase):
    def setUp(self):
        self.default_function = PeripheralSolution._get_gene_name
        self.headers = ["source", "lambda", "vmax", "TF1", "TF2", "TF3"]

    def tearDown(self):
        PeripheralSolution._get_gene_name = self.default_function

    def test_RaisesException(self):
        assert_raises(RuntimeError, create_fake_solution, 10)

    def test_DifferentGenes(self):
        PeripheralSolution._get_gene_name = lambda x: "gene1"
        solution1 = create_fake_solution(10)
        PeripheralSolution._get_gene_name = lambda x: "gene2"
        solution2 = create_fake_solution(10)
        assert_not_equal(solution1.gene_name, solution2.gene_name,
                         "Expected different gene name but received the same")

    def test_SameGene(self):
        PeripheralSolution._get_gene_name = lambda x: "gene"
        solution1 = create_fake_solution(10)
        solution2 = create_fake_solution(11)
        assert_equal(solution1.gene_name, solution2.gene_name,
                     "Expected same gene name but received a different one")

    def test_SolutionMatrix(self):
        PeripheralSolution._get_gene_name = lambda x: "gene"
        solution = create_fake_solution(10)
        data = np.array(["gene", 1.0, 1.5, 10.0, 0.0, 21.0])
        expected = pd.Series(data, self.headers).to_frame().transpose()
        actual = solution.get_solution_matrix(self.headers)
        pdt.assert_frame_equal(expected, actual)

    def test_JoinMultipleSolutions(self):
        PeripheralSolution._get_gene_name = lambda x: "gene1"
        solution1 = create_fake_solution(10)
        PeripheralSolution._get_gene_name = lambda x: "gene2"
        solution2 = create_fake_solution(10)
        PeripheralSolution._get_gene_name = lambda x: "gene3"
        solution3 = create_fake_solution(10)

        expected = pd.DataFrame(
            data=np.array([["gene1", 1.0, 1.5, 10.0, 0.0, 21.0],
                           ["gene2", 1.0, 1.5, 10.0, 0.0, 21.0],
                           ["gene3", 1.0, 1.5, 10.0, 0.0, 21.0]]),
            columns=self.headers
        )
        actual = pd.concat([solution1.get_solution_matrix(self.headers),
                            solution2.get_solution_matrix(self.headers),
                            solution3.get_solution_matrix(self.headers)],
                           ignore_index=True)
        pdt.assert_frame_equal(expected, actual)
