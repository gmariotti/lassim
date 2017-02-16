import os
import shutil
from collections import namedtuple
from unittest import TestCase

import numpy as np
from PyGMO.core import champion
from nose.tools import assert_list_equal, assert_raises
from sortedcontainers import SortedDict, SortedList, SortedSet

from core.handlers.csv_handlers import DirectoryCSVSolutionsHandler, \
    serialize_solution, SimpleCSVSolutionsHandler
from core.solutions.core_solution import CoreSolution

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def create_fake_solution(cost: float) -> CoreSolution:
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

    return CoreSolution(
        fake_champion, fake_reactions,
        FakeProblem(fake_k_react[0], fake_k_react[1])
    )


class TestSerializeFunction(TestCase):
    def setUp(self):
        self.output_dir = "test-output-dir"
        self.headers = ["lambda", "vmax", "GATA3", "STAT6", "MAF"]
        self.solutions = SortedList(
            [create_fake_solution(20), create_fake_solution(21.35)]
        )

        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

    def tearDown(self):
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_SerializeTop3Solutions(self):
        self.solutions.add(create_fake_solution(100))
        self.solutions.add(create_fake_solution(101))
        filename = "top3.csv"
        for i in range(3):
            serialize_solution(
                self.solutions[i], filename, self.output_dir,
                self.headers
            )

        expected = ["lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t20.0\n",
                    "lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t21.35\n",
                    "lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t100.0\n", ]
        with open(self.output_dir + "/" + filename) as output:
            actual = [line for line in output]

        assert_list_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_SerializeMultipleSolutionsWithoutAppend(self):
        self.solutions.add(create_fake_solution(100))
        self.solutions.add(create_fake_solution(101))
        filename = "top3.csv"
        for i in range(3):
            serialize_solution(
                self.solutions[i], filename, self.output_dir,
                self.headers, append=False
            )

        expected = ["lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t100.0\n", ]
        with open(self.output_dir + "/" + filename) as output:
            actual = [line for line in output]

        assert_list_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_SerializeMultipleSolutionsWithException(self):
        self.solutions.add(create_fake_solution(100))
        self.solutions.add(create_fake_solution(101))
        filename = "top3.csv"
        serialize_solution(
            self.solutions[0], filename, self.output_dir,
            self.headers
        )
        assert_raises(
            RuntimeWarning, serialize_solution, self.solutions[1],
            filename, self.output_dir, self.headers, override=False
        )


class TestSimpleCSVSolutionsHandler(TestCase):
    def setUp(self):
        self.output_dir = "test-output-dir"
        self.number_of_solutions = 3
        self.headers = ["lambda", "vmax", "GATA3", "STAT6", "MAF"]
        self.handler = SimpleCSVSolutionsHandler(
            self.output_dir, self.number_of_solutions, self.headers,
            lambda x, y: "top3.csv"
        )
        self.solutions = SortedList(
            [create_fake_solution(20), create_fake_solution(21.35)]
        )

    def tearDown(self):
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_SerializeTop3ButSolutionsAreJust2(self):
        self.handler.handle_solutions(self.solutions)

        expected = ["lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t20.0\n",
                    "lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t21.35\n"]
        with open(self.output_dir + "/" + "top3.csv") as output:
            actual = [line for line in output]

        assert_list_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_DefaultFilenameCreator(self):
        handler = SimpleCSVSolutionsHandler(
            self.output_dir, 2, self.headers
        )
        handler.handle_solutions(self.solutions)
        expected = ["lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t20.0\n",
                    "lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t21.35\n"]
        filename = "top2solutions_9variables_{}.csv".format(os.getpid())
        csv_file = self.output_dir + "/" + filename
        with open(csv_file) as output:
            actual = [line for line in output]

        assert_list_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_CustomFilename(self):
        self.handler.handle_solutions(
            self.solutions, "custom-filename.csv"
        )
        expected = ["lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t20.0\n",
                    "lambda\tvmax\tGATA3\tSTAT6\tMAF\n",
                    "1.0\t2.0\t0.0\t0.0\t0.0\n",
                    "1.5\t2.5\t1.0\t0.0\t1.0\n",
                    "0.0\t5.0\t0.0\t0.0\t1.0\n",
                    "Cost\t21.35\n"]
        csv_file = self.output_dir + "/" + "custom-filename.csv"
        with open(csv_file) as output:
            actual = [line for line in output]

        assert_list_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))


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
        inner_dir = "9_vars_top2"
        self.handler.handle_solutions(self.solutions, inner_dir)
        expected_dir = self.directory + "/" + inner_dir
        if not os.path.isdir(expected_dir):
            self.fail("Expected directory {} not found".format(expected_dir))

        expected_files = ["best_1.csv", "best_2.csv"]
        actual_files = os.listdir(expected_dir)
        actual_files.sort()
        assert_list_equal(expected_files, actual_files,
                          "Expected files\n{}\nbut actual\n{}".format(
                              expected_files, actual_files
                          ))
