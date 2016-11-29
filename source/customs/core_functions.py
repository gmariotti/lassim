import logging
from copy import deepcopy
from typing import List

import numpy as np
from sortedcontainers import SortedDict

from core.core_problem import CoreProblemFactory
from core.lassim_problem import LassimProblem
from core.solutions.lassim_solution import LassimSolution
from core.utilities.type_aliases import Vector, Float

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"


def default_bounds(num_tfacts: int, num_react: int
                   ) -> (List[float], List[float]):
    """
    Creates a tuple containing as first element the list of lower bounds, and as
    second element the list of upper bounds for the parameter to optimize.
    By default, for lambda/vmax the bounds are (0, 20), while for the k are
    (-20, 20)
    :param num_tfacts: Number of transcription factors in the network
    :param num_react: Number of reactions between the transcription factors
    :return: Tuple contains lower bounds list and upper bounds list
    """
    # FIXME - no smarter way to do this?
    lower_bounds = [0.0 for _ in range(0, num_tfacts * 2)]
    upper_bounds = [20.0 for _ in range(0, num_tfacts * 2 + num_react)]
    for _ in range(0, num_react):
        lower_bounds.append(-20.0)
    return lower_bounds, upper_bounds


def generate_reactions_vector(reactions: SortedDict, dt_react=Float
                              ) -> (Vector, Vector):
    """
    From a reactions map, generates the corresponding numpy vector for
    reactions and its boolean mask. The reaction vector contains #tfacts**2
    elements, and each #tfacts subset represent the list of reactions with
    other transcription factors for one of them. The values are 0 if the
    reaction is not present and -1 if it is.
    :param reactions: map of transcription factors and their reactions
    :param dt_react: type of vector values
    :return: numpy array for reactions and its corresponding boolean mask
    """
    reacts = []
    num_tfacts = len(reactions.keys())
    for tfact, reactions in reactions.items():
        vector = np.zeros(num_tfacts)
        vector[reactions] = -1
        reacts.append(vector.tolist())
    reacts_flatten = [val for sublist in reacts for val in sublist]
    np_reacts = np.array(reacts_flatten, dtype=dt_react)
    bool_mask = np_reacts < 0

    return np_reacts, bool_mask


def remove_lowest_reaction(vres: Vector, reactions: SortedDict
                           ) -> (Vector, SortedDict):
    """
    Searches in the optimization result vector vres, which reaction as the
    lowest |val| and removes it. From that index, removes the reaction also
    from the reactions map
    :param vres: result of the optimization
    :param reactions: map of reactions by ids
    :return: result without the lowest |val| and the new reactions map
    """
    tfacts_num = len(reactions.keys())
    k_values = vres[tfacts_num * 2:]
    abs_k = np.absolute(k_values)
    min_index = np.argmin(abs_k)
    if min_index.size > 1:
        min_index = min_index[0]
    reactions = deepcopy(reactions)

    # for each transcription factors and its reactions, count is increased
    # until min_index is found, in order to find each reaction to remove. The
    #  main reaction map is not modified because I'm working on the id one
    # that is dynamically built every time
    count = 0
    for i in range(0, tfacts_num):
        count += len(reactions[i])
        if count > min_index:
            # this transcription factor is the one containing the reaction to
            #  remove
            index = min_index - count + len(reactions[i])
            value = reactions[i].pop(index)
            logging.getLogger(__name__).info(
                "Removed connection={} from reaction={}".format(value, i)
            )
            return np.delete(vres, min_index + tfacts_num * 2), reactions
    raise IndexError("Index {} to remove not found!!".format(min_index))


# FIXME - move to a default file not related to the Core
def iter_function(factory: CoreProblemFactory, solution: LassimSolution
                  ) -> (LassimProblem, SortedDict, bool):
    react_mask = solution.react_mask
    # checks how many true are still present in the reaction mask. If > 0, it
    # means that there's still at least a reaction
    if react_mask[react_mask].size > 0:
        reactions = solution.reactions_ids
        reduced_vect, new_reactions = remove_lowest_reaction(
            solution.solution_vector, reactions
        )
        new_react, new_mask = generate_reactions_vector(new_reactions)
        num_react = new_react[new_mask].size
        new_problem = factory.build(
            dim=len(new_reactions.keys()) * 2 + num_react,
            bounds=default_bounds(len(new_reactions.keys()), num_react),
            vector_map=(new_react, new_mask), known_sol=[reduced_vect]
        )
        return new_problem, new_reactions, True
    else:
        return None, None, False
