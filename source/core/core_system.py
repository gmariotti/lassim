from sortedcontainers import SortedDict, SortedSet

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


# TODO - consider the possibility of a factory method for creating a new
# CoreSystem starting from the map of reactions. Should it be a static
# method? Or can be exploited the list of tfacts of an existing object?
class CoreSystem:
    def __init__(self, network: SortedDict, correction: bool = True):
        """
        Network must be something generated by the reading of the file with
        the transcription factor, in the form of a dictionary
        :param network: dictionary with, for each transcription factor,
        the set of transcription factors on which has influence
        :param correction: decides if transcription factors with no reactions
        must be "corrected" or not with a reaction with all the other
        transcription factors plus itself
        """
        self._network = network
        self.tfacts = SortedSet(network.keys()).union(
            {tfact for tflist in network.viewvalues() for tfact in tflist}
        )
        self.__reactions, self.__react_count = self.__reactions_from_network(
            correction
        )

    def __reactions_from_network(self, correction: bool) -> (SortedDict, int):
        """
        The dictionary of reactions returned is reversed in respect to the
        network one. Each transcription factor has the set of transcription
        factors that affect him
        :param correction: decides if transcription factors with no reactions
        must be "corrected" or not with a reaction with all the other
        transcription factors plus itself
        :return: reactions dictionary and number of reactions
        """
        reactions_sorted = SortedDict()
        reactions_count = 0
        for tfact, reactions in self._network.items():
            # in this way, even if a transcription factor is not influenced
            # by anyone, is still have is empty set of reactions
            if tfact not in reactions_sorted:
                reactions_sorted[tfact] = SortedSet()

            for reaction in reactions:
                if reaction not in reactions_sorted:
                    reactions_sorted[reaction] = SortedSet()
                reactions_sorted[reaction].add(tfact)
                reactions_count += 1

        if correction:
            # for each empty set, all the transcription factors are added
            for tfact, reactions in reactions_sorted.items():
                if len(reactions) == 0:
                    reactions_sorted[tfact] = SortedSet(self.tfacts)
                    reactions_count += len(self.tfacts)

        return reactions_sorted, reactions_count

    def from_tfacts_to_ids(self) -> (str, int):
        """
        Maps each transcription factor to an id, starting from 0 until
        len(tfacts) - 1
        :return: (tfact, id)
        """
        for i in range(0, len(self.tfacts)):
            yield self.tfacts[i], i

    def from_ids_to_tfacts(self) -> (str, int):
        """
        Maps each id to its transcription factor. Result is always the same
        because the transcription factors are an ordered set
        :return: (id, tfact)
        """
        for i in range(0, len(self.tfacts)):
            yield i, self.tfacts[i]

    def from_reactions_to_ids(self) -> (int, SortedSet):
        """
        Maps each reaction with its corresponding id.
        :return: (id, set(reactions_ids))
        """
        tfacts_ids = {key: value for key, value in self.from_tfacts_to_ids()}
        for tfact, reactions in self.reactions.items():
            reactions_ids = SortedSet([tfacts_ids[tf] for tf in reactions])
            yield tfacts_ids[tfact], reactions_ids

    def from_reactions_ids_to_str(self, reactions: SortedDict
                                  ) -> (str, SortedSet):
        """
        Maps a dictionary of reactions from ids to string names.
        :param reactions: Dictionary of <int:set(int)> representing reactions as
        integer numbers
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
    def num_tfacts(self):
        return len(self.tfacts)

    @property
    def reactions(self):
        return self.__reactions

    @property
    def react_count(self):
        return self.__react_count

    def __str__(self):
        title = "== Core =="
        tfacts_title = "= List of transcription factors ="
        tfacts = ", ".join(self.tfacts)
        reactions_title = "= List of reactions ="
        reactions = "\n".join([key + " --> " + ", ".join(value)
                               for key, value in self.reactions.viewitems()])
        return "\n".join(
            [title, tfacts_title, tfacts, reactions_title, reactions]
        )
