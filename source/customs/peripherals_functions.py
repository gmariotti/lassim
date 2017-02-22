import logging
from copy import deepcopy
from typing import Tuple, Callable, Optional

import numpy as np
from sortedcontainers import SortedDict
from sortedcontainers import SortedSet

from core.problems.network_problem import NetworkProblemFactory, NetworkProblem
from core.solutions.peripheral_solution import PeripheralSolution
from core.utilities.type_aliases import Vector, Tuple2V, Float

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

"""
Set of custom functions for peripherals problem creation and iteration.
"""


def default_bounds(num_genes: int, num_react: int):
    """
    Creates a tuple containing as first element the list of lower bounds, and as
    second element the list of upper bounds for the parameter to optimize.
    By default, for lambda/vmax the bounds are (0, 20), while for the k are
    (-20, 20)

    :param num_genes: Number of genes in the network.
    :param num_react: Number of reactions between genes and transcription
        factors core.
    :return: Tuple containing the lower bounds list and upper bounds list.
    """

    lower_bounds = [0.0 for _ in range(0, num_genes * 2)]
    upper_bounds = [20.0 for _ in range(0, num_genes * 2 + num_react)]
    for _ in range(0, num_react):
        lower_bounds.append(-20.0)
    return lower_bounds, upper_bounds


def remove_lowest_reaction(solution_vector: Vector, reactions: SortedSet,
                           gene: str) -> Tuple[Vector, SortedSet]:
    """
    From a solution vector removes the reaction with the lowest absolute value
    and generates a new dictionary with all the reactions except the one
    removed.

    :param solution_vector: The numpy.ndarray representing an optimization
        solution.
    :param reactions: The set of reactions for a gene.
    :param gene: Name of the current gene.
    :return: Tuple containing the solution_vector and the reactions set
        without the reaction removed.
    """

    absolute_k = np.absolute(solution_vector[2:])
    min_index = np.argmin(absolute_k)
    if min_index.size > 1:
        min_index = min_index[0]
    reactions = deepcopy(reactions)

    try:
        val_removed = reactions.pop(min_index)
        logging.getLogger(__name__).info(
            "Removed connection={} from gene={}".format(val_removed, gene)
        )
        index_to_remove = min_index + 2
        return np.delete(solution_vector, index_to_remove), reactions
    except IndexError:
        raise IndexError("Index {} to remove not found!!".format(min_index))


# FIXME
def generate_core_vector(core_data: Vector, num_tf: int,
                         genes_reactions: SortedSet) -> Tuple2V:
    """
    Used for generating a core vector needed in NetworkProblem instances. Core
    reactions not present.

    :param core_data: Represents the data for the core system. It must be a 2D
        matrix, with each row representing the data for a transcription factor.
        Each row must be in the format: [lambda, vmax, k1,...,kn]
    :param num_tf: Number of transcription factors in the core.
    :param genes_reactions: Dictionary containing the reactions between the
        genes and the core.
    :return: Tuple containing a vector in the format:
        [lambda_1,..,lambda_#tf, lambda_gene,
        vmax_1,..,vmax_#tf,vmax_gene,
        react_gene1,..,react_gene#tf] and its boolean mask for discriminating
        the genes data. Each data related to the core is the one from the
        core_data, while the data related to the gene are all set to numpy.inf.
        The mask represents which data are numpy.inf and which are not.
    """

    # is the same value for vmax
    tot_lambdas = num_tf + 1
    # the peripheral can have max num_tf reactions
    num_genes_reactions = len(genes_reactions)
    core_vector = np.zeros(tot_lambdas * 2 + num_genes_reactions)

    # changes the values of lambdas and vmax with the one in the core data
    core_vector[:num_tf] = core_data[:, 0]
    core_vector[num_tf + 1: num_tf * 2 + 1] = core_data[:, 1]

    # changes the values for the genes data to 0
    # in order lambda, vmax and num_tf*reactions
    core_vector[num_tf: num_tf + 1] = np.inf
    core_vector[num_tf * 2 + 1: num_tf * 2 + 2] = np.inf
    core_vector[num_tf * 2 + 2:] = np.inf

    return core_vector, core_vector == np.inf


def generate_reactions_vector(gene_reactions: SortedSet, core_data: Vector,
                              num_tf: int, dt_react=Float) -> Tuple2V:
    """
    From a reactions map and the core data, generates the corresponding numpy
    vector for the reactions of core and genes and its boolean mask. The
    reaction vector contains #tfacts^2 + #tfacts*#genes elements, and each
    #tfacts subset represent the list of reactions with the transcription
    factors. The values are 0 if the reaction is not present and numpy.inf
    if it is.

    :param gene_reactions: Set of reactions for a gene in respect to the core.
    :param core_data: Represents the data for the core system. It must be a 2D
        matrix, with each row representing the data for a transcription factor.
        Each row must be in the format: [lambda, vmax, k1,...,kn]
    :param num_tf: Number of transcription factors in the core.
    :param dt_react: The type of numpy array you want to build.
    :return: Tuple containing the reaction vector and its corresponding mask.
    """

    reacts = []
    vector = np.zeros(num_tf + 1, dtype=dt_react)
    vector[gene_reactions] = np.inf
    reacts.append(vector.tolist())
    # adds an extra reaction set to 0 in each row
    core_data = np.insert(core_data, num_tf + 2, 0, axis=1)
    core_reacts_flatten = [val for row in core_data
                           for val in row[2:]]
    np_reacts = np.array(
        core_reacts_flatten + vector.tolist(), dtype=dt_react
    )

    return np_reacts, np_reacts == np.inf


def iter_function(core_data: Vector, num_tf: int, num_core_react: int
                  ) -> Callable[[NetworkProblemFactory, PeripheralSolution],
                                Tuple[Optional[NetworkProblem],
                                      SortedDict, bool]]:
    """
    This function returns a custom function for performing an iteration after
    a completed optimization for a certain number of variables in the network.
    This function generates a new problem to solve, with one less variable, a
    new dictionary of reactions and a boolean value in case the optimization
    should continue or not. The reaction removed from the old problem is the
    one with the lowest absolute value.

    :param core_data: Represents the data for the core system. It must be a 2D
        matrix, with each row representing the data for a transcription factor.
        Each row must be in the format:
        [lambda, vmax, k1,...,kn]
    :param num_tf: Number of transcription factors in the core.
    :param num_core_react: Number of reactions in the core.
    :return: Iteration function that accept as input a NetworkProblemFactory and
        the PeripheralSolution to evaluate.
    """

    def wrapper(factory: NetworkProblemFactory, solution: PeripheralSolution
                ) -> Tuple[Optional[NetworkProblem], SortedDict, bool]:
        react_mask = solution.react_mask
        if react_mask[react_mask].size > 0:
            # it means that at least one reaction is present
            # FIXME - reactions are SortedSet and are converted to SortedDict
            # at the end
            reactions = solution.reactions_ids
            reduced_vect, new_reactions = remove_lowest_reaction(
                solution.solution_vector, reactions, solution.gene_name
            )
            new_core, core_mask = generate_core_vector(
                core_data, num_tf, reactions
            )
            new_react, new_mask = generate_reactions_vector(
                new_reactions, core_data, num_tf
            )
            num_genes_reactions = len(new_reactions)

            new_problem = factory.build(
                dim=2 + num_genes_reactions,
                bounds=default_bounds(1, num_genes_reactions),
                vector_map=(new_react, new_mask), known_sol=[reduced_vect],
                core_data=(new_core, core_mask)
            )
            gene_reactions_dict = SortedDict({
                solution.gene_name: new_reactions
            })
            return new_problem, gene_reactions_dict, True
        else:
            return None, SortedDict(), False

    return wrapper
