from typing import NamedTuple, List

from sortedcontainers import SortedDict

from core.utilities.type_aliases import Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

InputFiles = NamedTuple(
    "InputFiles", [("network", str), ("data", List[str]), ("times", str),
                   ("perturbations", str)]
)

InputExtra = NamedTuple(
    "InputExtra", [("core", str), ("num_cores", int), ("core_pert", str),
                   ("core_y0", str)]
)

OutputData = NamedTuple(
    "OutputData", [("directory", str), ("num_solutions", int)]
)

CoreData = NamedTuple(
    "CoreData", [("data", Vector), ("sigma", Vector), ("times", Vector),
                 ("perturb", Vector), ("y0", Vector)]
)

PeripheralsData = NamedTuple(
    "PeripheralsData", [("core_data", CoreData), ("pert_gene", Vector),
                        ("num_genes", int), ("num_react", int),
                        ("reactions", SortedDict)]
)
