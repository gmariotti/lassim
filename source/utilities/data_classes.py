from typing import NamedTuple, List

from sortedcontainers import SortedDict

from core.utilities.type_aliases import Vector

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.3.0"

InputFiles = NamedTuple(
    "InputFiles",
    [("network", str), ("data", List[str]), ("times", str),
     ("perturbations", str)]
)

CoreFiles = NamedTuple(
    "CoreFiles",
    [("core_system", str), ("core_pert", str), ("core_y0", str)]
)

OutputFiles = NamedTuple(
    "OutputFiles",
    [("directory", str), ("num_solutions", int)]
)

InputExtra = NamedTuple(
    "InputExtra",
    [("num_tasks", int)]
)

CoreData = NamedTuple(
    "CoreData",
    [("data", Vector), ("sigma", Vector), ("times", Vector),
     ("perturb", Vector), ("y0", Vector)]
)

PeripheralData = NamedTuple(
    "PeripheralData",
    [("data", Vector), ("sigma", Vector), ("times", Vector),
     ("perturb", Vector), ("y0", Vector)]
)

PeripheralWithCoreData = NamedTuple(
    "PeripheralWithCoreData",
    [("peripheral_data", PeripheralData),
     ("core_data", Vector), ("core_pert", Vector),
     ("y0_combined", Vector), ("num_react", int), ("reactions", SortedDict)]
)
