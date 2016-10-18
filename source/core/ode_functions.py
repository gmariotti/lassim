from typing import Tuple

from scipy import integrate

from core.common_functions import function_integrate
from utilities.type_aliases import Vector

"""
This module offer a common interface for the different type of ode offered in
the scipy.integrate module. From scipy documentation, odeint, vode and zvode are
not considered thread-safe, but if the problem to optimize is implemented in
Python, then each new island/thread has its own Python interpreter, so there
won't be any problem.
"""

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1"


# TODO - because are strictly related to function_integrate, consider the
# TODO - possibility to move them somewhere else or doing them more generic

# FIXME - other frameworks can be available, search for them.

def odeint1e8_function(y0: Vector, t: Vector,
                       args: Tuple[Vector, Vector, Vector, int]) -> Vector:
    return integrate.odeint(function_integrate, y0, t, args=args,
                            mxstep=int(1e8))


def ode_vode_function(y0: Vector, t: Vector,
                      args: Tuple[Vector, Vector, Vector, int]) -> Vector:
    raise NotImplementedError(ode_vode_function.__name__)
