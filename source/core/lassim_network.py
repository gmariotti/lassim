from copy import deepcopy
from typing import Tuple, Iterator

from sortedcontainers import SortedDict, SortedSet

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


class LassimNetwork:
    @property
    def core(self) -> 'CoreSystem':
        """
        This method must be override when the Network interface is used.
        Depending on the class implementing this interface, this method must
        return the CoreSystem, or a subclass of it, representing that network.

        :return: The CoreSystem instance representing the network that
        overrides this method.
        """
        raise NotImplementedError(self.core.__name__)

    def from_reactions_to_ids(self) -> Iterator[Tuple[int, SortedSet]]:
        """
        This method must be override when the Network interface is used.
        Depending on the class implementing this interface, this method must
        return a generator mapping a gene, a transcription factor, or something
        else, to the corresponding set of reactions, interactions, ...

        :return: An Iterator that returns always a (id, set(reactions_ids))
        tuple.
        """

        raise NotImplementedError(self.from_reactions_to_ids.__name__)


class CoreSystem(LassimNetwork):
    def __init__(self, net_dict: SortedDict, correction: bool = True):
        """
        Network must be something generated by the reading of the file with
        the transcription factor, in the form of a dictionary.

        :param net_dict: Dictionary with, for each transcription factor,
        the set of transcription factors on which it has influence.
        :param correction: Decides if transcription factors with no reactions
        must be "corrected" or not with a reaction with all the other
        transcription factors plus itself.
        """
        self._network_dict = net_dict
        self.__tfacts = net_dict.keys()
        self.__reactions, self.__react_count = self.__reactions_from_network(
            correction
        )

    @classmethod
    def generate_core(cls, reactions: SortedDict) -> 'CoreSystem':
        """
        Generates a CoreSystem using the dictionary of reactions given as input.

        :param reactions: A dictionary containing for each transcription factor
        the set of genes from which is it influenced.
        :return: the corresponding CoreSystem
        """
        network = SortedDict()
        for react_tfact, influenced_set in reactions.viewitems():
            network.setdefault(react_tfact, default=SortedSet())
            for tfact in influenced_set:
                influencer_set = network.setdefault(tfact, default=SortedSet())
                influencer_set.add(react_tfact)
        core = CoreSystem(network, correction=False)

        return core

    def __reactions_from_network(self, correction: bool
                                 ) -> Tuple[SortedDict, int]:
        """
        The dictionary of reactions returned is reversed in respect to the
        network one. Each transcription factor has the set of transcription
        factors that affect him.

        :param correction: Decides if transcription factors with no reactions
        must be "corrected" or not with a reaction with all the other
        transcription factors plus itself.
        :return: Reactions dictionary and number of reactions.
        """
        reactions_sorted = SortedDict()
        reactions_count = 0
        for tfact, reactions in self._network_dict.items():
            # in this way, even if a transcription factor is not influenced
            # by anyone, is still have is empty set of reactions
            reactions_sorted.setdefault(tfact, default=SortedSet())

            for react_tfact in reactions:
                react_set = reactions_sorted.setdefault(
                    react_tfact, default=SortedSet()
                )
                react_set.add(tfact)
                reactions_count += 1

        if correction:
            # for each empty set, all the transcription factors are added
            for tfact, reactions in reactions_sorted.items():
                if len(reactions) == 0:
                    reactions_sorted[tfact] = SortedSet(self.tfacts)
                    reactions_count += len(self.tfacts)

        return reactions_sorted, reactions_count

    def from_tfacts_to_ids(self) -> Iterator[Tuple[str, int]]:
        """
        Maps each transcription factor to an id, starting from 0 until
        len(tfacts) - 1.

        :return: An Iterator that returns always a (tfact, id) tuple.
        """
        for i in range(0, len(self.tfacts)):
            yield self.tfacts[i], i

    def from_ids_to_tfacts(self) -> Iterator[Tuple[str, int]]:
        """
        Maps each id to its transcription factor. Result is always the same
        because the transcription factors are an ordered set.

        :return: An Iterator that returns always a (id, tfact) tuple.
        """
        for tfact, ident in self.from_tfacts_to_ids():
            yield ident, tfact

    def from_reactions_to_ids(self) -> Iterator[Tuple[int, SortedSet]]:
        """
        Maps each reaction with its corresponding id.

        :return: An Iterator that returns always a (id, set(reactions_ids))
        tuple.
        """
        tfacts_ids = {key: value for key, value in self.from_tfacts_to_ids()}
        for tfact, reactions in self.reactions.viewitems():
            reactions_ids = SortedSet([tfacts_ids[tf] for tf in reactions])
            yield tfacts_ids[tfact], reactions_ids

    def from_reactions_ids_to_str(self, reactions: SortedDict
                                  ) -> Iterator[Tuple[str, SortedSet]]:
        """
        Maps a dictionary of reactions from ids to string names.

        :param reactions: Dictionary of <int:set(int)> representing reactions as
        integer numbers.
        :return: The same dictionary as input with string names instead of
        integer ids.
        """
        tfacts_ids = {key: value for key, value in self.from_ids_to_tfacts()}
        for key, value in reactions.viewitems():
            try:
                react_set = SortedSet([tfacts_ids[val] for val in value])
                yield tfacts_ids[key], react_set
            except AttributeError:
                raise AttributeError(
                    "Value in key and/or value not present in core\nkey -> {}\n"
                    "value -> {}".format(key, value)
                )

    @property
    def core(self) -> 'CoreSystem':
        return self

    @property
    def tfacts(self) -> SortedSet:
        return SortedSet(self.__tfacts)

    @property
    def num_tfacts(self) -> int:
        return len(self.tfacts)

    @property
    def reactions(self) -> SortedDict:
        return deepcopy(self.__reactions)

    @property
    def react_count(self) -> int:
        return self.__react_count

    def __str__(self) -> str:
        title = "== Core =="
        tfacts_title = "= List of transcription factors ="
        tfacts = ", ".join(self.tfacts)
        reactions_title = "= List of reactions ="
        reactions = "\n".join([key + " --> " + ", ".join(value)
                               for key, value in self.reactions.viewitems()])
        return "\n".join(
            [title, tfacts_title, tfacts, reactions_title, reactions]
        )

    __repr__ = __str__


class NetworkSystem(LassimNetwork):
    def __init__(self, genes_net: SortedDict, core: CoreSystem,
                 correction: bool = True):
        """
        Construct a NetworkSystem object as a CoreSystem plus the network of
        genes on which the CoreSystem has influence to.

        :param genes_net: A dictionary containing the name/id of the gene as a
        key and the set of transcription factors that regulates it as value.
        :param core: A CoreSystem instance containing the Core of this network.
        :param correction: To be used in case genes with no transcription
        factors in their set should have a new set with all the transcription
        factors in the core.
        """
        self._network = genes_net
        self._genes = genes_net.keys()
        self._core = core
        self.__reactions, self.__react_count = self.__network_to_core_reactions(
            correction
        )

    def __network_to_core_reactions(self, correction: bool
                                    ) -> Tuple[SortedDict, int]:
        count = 0
        tfacts = self.core.tfacts
        reactions = SortedDict()
        for gene, gene_reacts in self._network.viewitems():
            react_set = reactions.setdefault(gene, default=SortedSet())
            for tfact in gene_reacts:
                # for each gene, adds to the set of reactions only valid
                # transcription factors
                if tfact in tfacts:
                    react_set.add(tfact)
                    count += 1
            if correction and len(react_set) == 0:
                reactions[gene] = self.core.tfacts
                count += len(tfacts)
        return reactions, count

    def from_genes_to_ids(self) -> Iterator[Tuple[str, int]]:
        """
        Maps each gene to an id, starting from len(tfacts) until
        len(tfacts) + len(genes) - 1.

        :return: An Iterator that returns always a (gene, id) tuple.
        """
        core = self.core
        num_tfacts = len(core.tfacts)
        num_genes = len(self.genes)
        for i in range(num_tfacts, num_tfacts + num_genes):
            yield self.genes[i - num_tfacts], i

    def from_ids_to_genes(self) -> Iterator[Tuple[str, int]]:
        """
        Maps each id to its gene. Result is always the same because the genes
        are in an ordered set.

        :return: An Iterator that returns always a (id, gene) tuple.
        """
        for gene, ident in self.from_genes_to_ids():
            yield ident, gene

    def from_reactions_to_ids(self) -> Iterator[Tuple[int, SortedSet]]:
        """
        Maps each reaction with its corresponding id.

        :return: An Iterator that returns always a (id, set(reactions_ids))
        tuple.
        """
        genes_ids = {key: value for key, value in self.from_genes_to_ids()}
        tfacts_dict = SortedDict(self.core.from_tfacts_to_ids())
        for gene, reactions in self.reactions.viewitems():
            reactions_ids = SortedSet([tfacts_dict[tf] for tf in reactions])
            yield genes_ids[gene], reactions_ids

    @property
    def core(self) -> CoreSystem:
        return self._core

    @property
    def genes(self) -> SortedSet:
        return SortedSet(self._genes)

    @property
    def reactions(self) -> SortedDict:
        return deepcopy(self.__reactions)

    @property
    def react_count(self) -> int:
        return self.__react_count
