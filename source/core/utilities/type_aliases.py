from typing import Tuple, NamedTuple

import numpy as np
from sortedcontainers import SortedDict

"""
Common type aliases used in the toolbox for improving readability.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

Vector = np.ndarray
Float = np.float64
# FIXME - replace them with the implementation commented near them
Tuple2V = Tuple[Vector, Vector]  # Tuple2[T] = Tuple[T, T]
Tuple3V = Tuple[Vector, Vector, Vector]  # Tuple3[T] = Tuple[T, T, T]
Tuple4V = Tuple[Vector, Vector, Vector, Vector]

# data types
CoreData = NamedTuple("CoreData",
                      [("data", Vector), ("sigma", Vector), ("times", Vector),
                       ("perturb", Vector), ("y0", Vector)])
PeripheralsData = NamedTuple("PeripheralsData",
                             [("core_data", CoreData), ("num_genes", int),
                              ("num_react", int), ("reactions", SortedDict)])
