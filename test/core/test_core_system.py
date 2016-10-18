from unittest import TestCase

from nose.tools import assert_dict_equal
from sortedcontainers import SortedDict, SortedSet

from core.core_system import CoreSystem

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


class TestCoreSystem(TestCase):
    def setUp(self):
        self.fake_network = SortedDict({
            "NFATC3": SortedSet(["IRF4", "MAF"]),
            "STAT3": SortedSet(["MAF"]),
            "IRF4": SortedSet(["MAF", "STAT3"]),
            "MAF": SortedSet()
        })

    def test_GenerationOfReactionsMap(self):
        expected_reactions = SortedDict({
            "NFATC3": SortedSet(["NFATC3", "IRF4", "MAF", "STAT3"]),
            "STAT3": SortedSet(["IRF4"]),
            "IRF4": SortedSet(["NFATC3"]),
            "MAF": SortedSet(["NFATC3", "STAT3", "IRF4"])
        })
        expected_count = 9
        core = CoreSystem(self.fake_network)
        actual_reactions, actual_count = core.reactions_from_network()

        expected = (expected_reactions, expected_count)
        actual = (actual_reactions, actual_count)
        self.assertTupleEqual(expected, actual,
                              "Expected\n{}\nbut actual\n{}".format(
                                  expected, actual
                              ))

    def test_DictionaryTFactToID(self):
        expected = SortedDict({
            "IRF4": 0,
            "MAF": 1,
            "NFATC3": 2,
            "STAT3": 3
        })
        core = CoreSystem(self.fake_network)
        actual = dict(core.from_tfacts_to_ids())
        assert_dict_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_DictionaryIDtoTFact(self):
        expected = SortedDict({
            0: "IRF4",
            1: "MAF",
            2: "NFATC3",
            3: "STAT3"
        })
        core = CoreSystem(self.fake_network)
        actual = dict(core.from_ids_to_tfacts())
        assert_dict_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))

    def test_ReactionsMapToIDs(self):
        expected = SortedDict({
            0: SortedSet([2]),
            1: SortedSet([0, 2, 3]),
            2: SortedSet([0, 1, 2, 3]),
            3: SortedSet([0])
        })
        core = CoreSystem(self.fake_network)
        actual = dict(core.from_reactions_to_ids())
        assert_dict_equal(expected, actual,
                          "Expected\n{}\nbut actual\n{}".format(
                              expected, actual
                          ))
