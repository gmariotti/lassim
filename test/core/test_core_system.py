from unittest import TestCase

from nose.tools import assert_dict_equal, assert_tuple_equal, assert_equal, \
    assert_raises
from sortedcontainers import SortedDict, SortedSet

from core.core_system import CoreSystem

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


class TestCoreSystem(TestCase):
    def setUp(self):
        self.fake_network = SortedDict({
            "NFATC3": SortedSet(["IRF4", "MAF"]),
            "STAT3": SortedSet(["MAF"]),
            "IRF4": SortedSet(["MAF", "STAT3"]),
            "MAF": SortedSet()
        })

    def test_GenerationOfReactionsMapWithCorrection(self):
        expected_reactions = SortedDict({
            "NFATC3": SortedSet(["NFATC3", "IRF4", "MAF", "STAT3"]),
            "STAT3": SortedSet(["IRF4"]),
            "IRF4": SortedSet(["NFATC3"]),
            "MAF": SortedSet(["NFATC3", "STAT3", "IRF4"])
        })
        expected_count = 9
        core = CoreSystem(self.fake_network)
        actual_reactions, actual_count = core.reactions_from_network(True)

        expected = (expected_reactions, expected_count)
        actual = (actual_reactions, actual_count)
        assert_tuple_equal(expected, actual,
                           "Expected\n{}\nbut actual\n{}".format(
                               expected, actual
                           ))

    def test_GenerationOfReactionsMapWithoutCorrection(self):
        expected_reactions = SortedDict({
            "NFATC3": SortedSet(),
            "STAT3": SortedSet(["IRF4"]),
            "IRF4": SortedSet(["NFATC3"]),
            "MAF": SortedSet(["NFATC3", "STAT3", "IRF4"])
        })
        expected_count = 5
        core = CoreSystem(self.fake_network)
        actual_reactions, actual_count = core.reactions_from_network(False)

        expected = (expected_reactions, expected_count)
        actual = (actual_reactions, actual_count)
        assert_tuple_equal(expected, actual,
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

    def test_FromReactionsIDsToStrMap(self):
        fake_reactions_ids = SortedDict({
            0: SortedSet([]),
            1: SortedSet([2, 3]),
            2: SortedSet([0, 1, 2]),
            3: SortedSet([])
        })
        expected = SortedDict({
            "IRF4": SortedSet(),
            "MAF": SortedSet(["NFATC3", "STAT3"]),
            "NFATC3": SortedSet(["IRF4", "MAF", "NFATC3"]),
            "STAT3": SortedSet()
        })
        core = CoreSystem(self.fake_network)
        actual = SortedDict(core.from_reactions_ids_to_str(fake_reactions_ids))
        assert_dict_equal(
            expected, actual, "Expected\n{}\nbut actual\n{}".format(
                expected, actual
            ))

    def test_FromReactionsIDsToStrMapException(self):
        fake_reactions_ids = SortedDict({
            0: SortedSet([]),
            1: SortedSet([2, 3]),
            2: SortedSet([0, 1, 2]),
            3: SortedSet([5])
        })
        core = CoreSystem(self.fake_network)
        assert_raises(
            AttributeError, SortedDict.__init__,
            core.from_reactions_ids_to_str, fake_reactions_ids,
        )

    def test_ToString(self):
        expected = "== Core ==\n" \
                   "= List of transcription factors =\n" \
                   "IRF4, MAF, NFATC3, STAT3\n" \
                   "= List of reactions =\n" \
                   "IRF4 --> NFATC3\n" \
                   "MAF --> IRF4, NFATC3, STAT3\n" \
                   "NFATC3 --> IRF4, MAF, NFATC3, STAT3\n" \
                   "STAT3 --> IRF4"
        core = CoreSystem(self.fake_network)
        actual = str(core)
        assert_equal(expected, actual, "Expected\n{}\nbut received\n{}".format(
            expected, actual
        ))
