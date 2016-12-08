import pandas as pd
from sortedcontainers import SortedDict, SortedSet

from core.lassim_network import NetworkSystem, CoreSystem
from data_management.csv_format import parse_core_data, parse_network

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"


def create_network(network_file: str, core_file: str) -> NetworkSystem:
    """
    Creates a NetworkSystem instance starting from its network file and the
    a file containing the data for the core.

    :param network_file: Path to the file containing the network info.
    :param core_file: Path to the file containing the core data.
    :return: NetworkSystem instance representing the given core and the
        corresponding network given as input.
    """
    core_data = parse_core_data(core_file)
    reactions = get_reactions_from_data(core_data)
    core = CoreSystem.generate_core(reactions)
    network = parse_network(network_file)

    return NetworkSystem(network, core)


def get_reactions_from_data(core_data: pd.DataFrame) -> SortedDict:
    """
    From a pandas.DataFrame extracts the map of reactions for each transcription
    factor. Is fundamental that the core_data has the headers lambda and vmax,
    and that missing reactions have value 0.

    :param core_data: pandas.DataFrame representing the data from a core.
    :return: SortedDict with values as <tfact:set(tfacts)>.
    """
    reactions = SortedDict()
    data = core_data.drop(["lambda", "vmax"], axis=1)
    columns = [*data.columns]
    for index, row in data.iterrows():
        series = row.mask(lambda x: x == 0).dropna()
        reactions[columns[index]] = SortedSet(*series.axes)

    return reactions
