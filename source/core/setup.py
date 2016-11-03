from distutils.core import setup
from distutils.extension import Extension

from Cython.Distutils import build_ext

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

compiler = {
    "build_ext": build_ext,
    "language_level": 3
}

extensions = [
    Extension("functions.perturbation_functions",
              ["functions/perturbation_functions.pyx"]),
    Extension("functions.ode_functions",
              ["functions/ode_functions.pyx"]),
    Extension("functions.common_functions",
              ["functions/common_functions.pyx"])
]

setup(
    cmdclass=compiler,
    ext_modules=extensions
)
