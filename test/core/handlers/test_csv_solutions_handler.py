import os
import shutil
from collections import namedtuple
from unittest import TestCase

import numpy as np
from PyGMO.core import champion
from nose.tools import assert_list_equal
from sortedcontainers import SortedDict, SortedList, SortedSet

from core.handlers.csv_handlers import DirectoryCSVSolutionsHandler
from core.solutions.lassim_solution import LassimSolution

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def create_fake_solution(cost: float) -> LassimSolution:
    # first six values are lambdas and vmax
    fake_champion = champion()
    fake_champion.x = (1, 1.5, 0, 2, 2.5, 5, 1, 1, 1)
    fake_champion.f = (cost,)
    fake_champion.c = ()
    fake_reactions = SortedDict({
        0: SortedSet(), 1: SortedSet([0, 2]), 2: SortedSet([2])
    })
    fake_k_react = (np.array([0, 0, 0, 1, 0, 1, 0, 0, 1], dtype=np.float64),
                    np.array([False, False, False, True, False, True,
                              False, False, True])
                    )
    # too lazy to create an entire CoreProblem
    FakeProblem = namedtuple("FakeProblem", ["vector_map", "vector_map_mask"])

    return LassimSolution(
        fake_champion, fake_reactions,
        FakeProblem(fake_k_react[0], fake_k_react[1])
    )


class TestDirectoryCSVSolutionsHandler(TestCase):
    def setUp(self):
        self.directory = "test_dir_csv"
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        self.handler = DirectoryCSVSolutionsHandler(
            self.directory, 2, ["lambda", "vmax", "GATA3", "STAT6", "MAF"]
        )
        self.solutions = SortedList(
            [create_fake_solution(20), create_fake_solution(21.35)]
        )

    def tearDown(self):
        if os.path.isdir(self.directory):
            shutil.rmtree(self.directory)

    def test_MultipleSolutionsInSameDirectory(self):
        self.handler.handle_solutions(self.solutions)
        expected_dir = self.directory + "/" + "9_vars_top2"
        if not os.path.isdir(expected_dir):
            self.fail("Expected directory {} not found".format(expected_dir))

        expected_files = ["best1.csv", "best2.csv"]
        actual_files = os.listdir(expected_dir)
        actual_files.sort()
        assert_list_equal(expected_files, actual_files,
                          "Expected files\n{}\nbut actual\n{}".format(
                              expected_files, actual_files
                          ))
