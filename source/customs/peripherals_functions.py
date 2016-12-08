import logging
from copy import deepcopy
from typing import Tuple, Callable, Optional

import numpy as np
from sortedcontainers import SortedDict

from core.problems.network_problem import NetworkProblemFactory, NetworkProblem
from core.solutions.lassim_solution import LassimSolution
from core.utilities.type_aliases import Vector, Tuple2V, Float

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


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


def remove_lowest_reaction(solution_vector: Vector, reactions: SortedDict
                           ) -> Tuple[Vector, SortedDict]:
    """
    From a solution vector removes the reaction with the lowest absolute value
    and generates a new dictionary with all the reactions except the one
    removed.

    :param solution_vector: The numpy.ndarray representing an optimization
        solution.
    :param reactions: A dictionary containing the set of reactions for each
        gene.
    :return: Tuple containing the solution_vector and the reactions dictionary
        without the reaction removed.
    """
    num_genes = len(reactions.keys())
    absolute_k = np.absolute(solution_vector[num_genes * 2:])
    min_index = np.argmin(absolute_k)
    if min_index.size > 1:
        min_index = min_index[0]
    reactions = deepcopy(reactions)

    count = 0
    for key, value in reactions.viewitems():
        if (min_index - count) < len(value):
            val_removed = value.pop(min_index - count)
            logging.getLogger(__name__).info(
                "Removed connection={} from gene={}".format(val_removed, key)
            )
            return np.delete(solution_vector, min_index + 2 * num_genes), reactions
        else:
            count += len(value)
    raise IndexError("Index {} to remove not found!!".format(min_index))


def generate_core_vector(core_data: Vector, num_tf: int, num_react_core: int,
                         genes_reactions: SortedDict) -> Tuple2V:
    """
    Used for generating a core vector needed in NetworkProblem instances.

    :param core_data: Represents the data for the core system. It must be a 2D
        matrix, with each row representing the data for a transcription factor.
        Each row must be in the format: [lambda, vmax, k1,...,kn]
    :param num_tf: Number of transcription factors in the core.
    :param num_react_core: Number of reactions inside the core.
    :param genes_reactions: Dictionary containing the reactions between the
        genes and the core.
    :return: Tuple containing a vector in the format:
        [lambda_1,..,lambda_#tf, lambda_g1, lambda_gm,
        vmax_1,..,vmax_#tf,vmax_g1,..,vmax_gn,
        react_1,..,react_#creact, react_g1,..,react_#greact] and this boolean mask.
        Each data related to the core is the one from the core_data, while the data
        related to genes are all set to numpy.inf. The mask represents which data
        are numpy.inf and which are not.
    """
    # is the same value for vmax
    num_genes = len(genes_reactions.keys())
    tot_lambdas = num_tf + num_genes
    num_genes_reactions = len([val
                               for gene_set in genes_reactions.values()
                               for val in gene_set])
    core_vector = np.zeros(
        tot_lambdas * 2 + num_react_core + num_genes_reactions
    )

    # change the values of lambdas and vmax with the one in the core data
    core_vector[:num_tf] = core_data[:, 0]
    core_vector[num_tf + num_genes: num_tf * 2 + num_genes] = core_data[:, 1]

    # set the values for k
    k_start = num_tf * 2 + num_genes * 2
    k_core = core_data[:, 2:]
    core_vector[k_start: k_start + num_react_core] = k_core[k_core != 0]

    # change the values for the genes data to np.inf
    core_vector[num_tf: num_tf + num_genes] = np.inf
    core_vector[num_tf * 2 + num_genes: k_start] = np.inf
    core_vector[k_start + num_react_core:] = np.inf

    return core_vector, core_vector == np.inf


def generate_reactions_vector(genes_reactions: SortedDict, core_data: Vector,
                              dt_react=Float) -> Tuple2V:
    """
    From a reactions map and the core data, generates the corresponding numpy
    vector for the reactions of core and genes and its boolean mask. The
    reaction vector contains #tfacts^2 + #tfacts*#genes elements, and each
    #tfacts subset represent the list of reactions with the transcription
    factors. The values are 0 if the reaction is not present and numpy.inf
    if it is.

    :param genes_reactions: Reactions map for the genes in respect to the core.
    :param core_data: Represents the data for the core system. It must be a 2D
        matrix, with each row representing the data for a transcription factor.
        Each row must be in the format: [lambda, vmax, k1,...,kn]
    :param dt_react: The type of numpy array you want to build.
    :return: Tuple containing the reaction vector and its corresponding mask.
    """
    reacts = []
    # number of rows is the number of transcription factors
    num_tf = core_data.shape[0]
    for gene, react_set in genes_reactions.iteritems():
        vector = np.zeros(num_tf, dtype=dt_react)
        vector[react_set] = np.inf
        reacts.append(vector.tolist())
    core_reacts_flatten = [val for row in core_data for val in row[2:]]
    reacts_flatten = [val for sublist in reacts for val in sublist]
    np_reacts = np.array(core_reacts_flatten + reacts_flatten, dtype=dt_react)

    return np_reacts, np_reacts == np.inf


def iter_function(core_data: Vector, num_tf: int, num_core_react: int
                  ) -> Callable[[NetworkProblemFactory, LassimSolution],
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
        the LassimSolution to evaluate.
    """

    def wrapper(factory: NetworkProblemFactory, solution: LassimSolution
                ) -> Tuple[Optional[NetworkProblem], SortedDict, bool]:
        react_mask = solution.react_mask
        if react_mask[react_mask].size > 0:
            # it means that at least one reaction is present
            reactions = solution.reactions_ids
            reduced_vect, new_reactions = remove_lowest_reaction(
                solution.solution_vector, reactions
            )
            new_core, core_mask = generate_core_vector(
                core_data, num_tf, num_core_react, new_reactions
            )
            new_react, new_mask = generate_reactions_vector(
                new_reactions, core_data
            )
            num_genes = len(new_reactions.keys())
            num_genes_reactions = len([react
                                       for r_set in new_reactions.values()
                                       for react in r_set])

            new_problem = factory.build(
                dim=num_genes * 2 + num_genes_reactions,
                bounds=default_bounds(num_genes, num_genes_reactions),
                vector_map=(new_react, new_mask), known_sol=[reduced_vect],
                core_data=(new_core, core_mask)
            )
            return new_problem, new_reactions, True
        else:
            return None, SortedDict(), False

    return wrapper
