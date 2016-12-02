from unittest import TestCase

from nose.tools import assert_dict_equal, assert_tuple_equal, assert_equal, \
    assert_raises
from nose.tools import assert_set_equal
from sortedcontainers import SortedDict, SortedSet

from core.lassim_network import CoreSystem, NetworkSystem

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class TestCoreSystem(TestCase):
    def setUp(self):
        self.fake_network = SortedDict({
            "NFATC3": SortedSet(["IRF4", "MAF"]),
            "STAT3": SortedSet(["MAF"]),
            "IRF4": SortedSet(["MAF", "STAT3"]),
            "MAF": SortedSet()
        })
        self.assert_message = "Expected\n{}\nbut actual\n{}"

    def test_GenerationOfReactionsMapWithCorrection(self):
        expected_reactions = SortedDict({
            "NFATC3": SortedSet(["NFATC3", "IRF4", "MAF", "STAT3"]),
            "STAT3": SortedSet(["IRF4"]),
            "IRF4": SortedSet(["NFATC3"]),
            "MAF": SortedSet(["NFATC3", "STAT3", "IRF4"])
        })
        expected_count = 9
        core = CoreSystem(self.fake_network)
        actual_reactions, actual_count = core.reactions, core.react_count

        expected = (expected_reactions, expected_count)
        actual = (actual_reactions, actual_count)
        assert_tuple_equal(expected, actual,
                           self.assert_message.format(
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
        core = CoreSystem(self.fake_network, False)
        actual_reactions, actual_count = core.reactions, core.react_count

        expected = (expected_reactions, expected_count)
        actual = (actual_reactions, actual_count)
        assert_tuple_equal(expected, actual,
                           self.assert_message.format(
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
                          self.assert_message.format(
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
                          self.assert_message.format(
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
                          self.assert_message.format(
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
        assert_dict_equal(expected, actual,
                          self.assert_message.format(
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
        assert_equal(expected, actual,
                     self.assert_message.format(
                         expected, actual
                     ))

    def test_GenerateCoreFromReactions(self):
        # these are the reactions from the network in setup without the
        # correction
        reactions = SortedDict({
            "NFATC3": SortedSet(),
            "STAT3": SortedSet(["IRF4"]),
            "IRF4": SortedSet(["NFATC3"]),
            "MAF": SortedSet(["NFATC3", "STAT3", "IRF4"])
        })
        core = CoreSystem.generate_core(reactions)
        expected_tfacts = SortedSet(["NFATC3", "STAT3", "IRF4", "MAF"])
        actual_tfacts = core.tfacts
        assert_set_equal(expected_tfacts, actual_tfacts,
                         self.assert_message.format(
                             expected_tfacts, actual_tfacts
                         ))
        actual_reactions = core.reactions
        assert_dict_equal(reactions, actual_reactions,
                          self.assert_message.format(
                              reactions, actual_reactions
                          ))


class TestNetworkSystem(TestCase):
    def setUp(self):
        core_network = SortedDict({
            "NFATC3": SortedSet(["IRF4", "MAF"]),
            "STAT3": SortedSet(["MAF"]),
            "IRF4": SortedSet(["MAF", "STAT3"]),
            "MAF": SortedSet()
        })
        self.core = CoreSystem(core_network)
        self.fake_genes_net = SortedDict({
            "1": SortedSet(),
            "10": SortedSet(["IRF4", "MAF"]),
            "14": SortedSet(["10"])
        })
        self.assert_message = "Expected\n{}\nbut actual\n{}"

    def test_NetworkSystemCreation(self):
        network = NetworkSystem(self.fake_genes_net, self.core)
        exp_reactions = SortedDict({
            "1": SortedSet(["NFATC3", "STAT3", "IRF4", "MAF"]),
            "10": SortedSet(["IRF4", "MAF"]),
            "14": SortedSet(["NFATC3", "STAT3", "IRF4", "MAF"])
        })
        exp_count = 10
        assert_dict_equal(exp_reactions, network.reactions,
                          self.assert_message.format(
                              exp_reactions, network.reactions
                          ))
        assert_equal(exp_count, network.react_count,
                     self.assert_message.format(
                         exp_count, network.react_count
                     ))

    def test_NetworkReactionsToIDs(self):
        network = NetworkSystem(self.fake_genes_net, self.core)
        expected = SortedDict({
            4: SortedSet([0, 1, 2, 3]),
            5: SortedSet([0, 1]),
            6: SortedSet([0, 1, 2, 3])
        })
        actual = SortedDict(network.from_reactions_to_ids())
        assert_dict_equal(expected, actual,
                          self.assert_message.format(
                              expected, actual
                          ))
