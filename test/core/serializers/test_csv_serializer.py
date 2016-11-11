import os
import shutil
from unittest import TestCase

import numpy as np
from PyGMO.core import champion
from nose.tools import assert_list_equal
from sortedcontainers import SortedList, SortedDict, SortedSet

from core.serializers.csv_serializer import CSVSerializer, \
    default_filename_creator
from core.solution import Solution


def create_fake_solution(cost: float) -> Solution:
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
    return Solution(fake_champion, fake_reactions, fake_k_react)


def fake_filename_creator(val1: int, val2: int):
    return "top3.csv"


class TestCSVSerializer(TestCase):
    def setUp(self):
        self.output_dir = "test-output-dir"
        self.number_of_solutions = 3
        self.headers = ["lambda", "vmax", "GATA3", "STAT6", "MAF"]
        self.serializer = CSVSerializer.new_instance(
            self.output_dir, self.number_of_solutions, self.headers,
            fake_filename_creator
        )
        self.solutions = SortedList(
            [create_fake_solution(20), create_fake_solution(21.35)]
        )

    def tearDown(self):
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_SerializeTop3Solutions(self):
        self.solutions.add(create_fake_solution(100))
        self.solutions.add(create_fake_solution(101))
        self.serializer.serialize_solutions(self.solutions)

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
        with open(self.output_dir + "/" + "top3.csv") as output:
            actual = [line for line in output]

        assert_list_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_SerializeTop3ButSolutionsAreJust2(self):
        self.serializer.serialize_solutions(self.solutions)

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
        serializer = CSVSerializer.new_instance(
            self.output_dir, 2, self.headers, default_filename_creator
        )
        serializer.serialize_solutions(self.solutions)
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
        csv_file = self.output_dir + "/" + "top2solutions_9variables.csv"
        with open(csv_file) as output:
            actual = [line for line in output]

        assert_list_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_CustomFilename(self):
        self.serializer.serialize_solutions(
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
