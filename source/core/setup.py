from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Build import cythonize
from Cython.Distutils import build_ext

__author__ = "Guido Pio Mariotti"
__copyright__ = "Copyright (C) 2016 Guido Pio Mariotti"
__license__ = "GNU General Public License v3.0"
__version__ = "0.1.0"

compiler = {
    # "profile": True,
    "build_ext": build_ext,
    "language_level": 3
}

extensions = [
    Extension("functions.perturbation_functions",
              ["functions/perturbation_functions.pyx"],
              # define_macros=[("CYTHON_TRACE", 1)],
              include_dirs=[numpy.get_include()]),
    Extension("functions.common_functions",
              ["functions/common_functions.pyx"],
              include_dirs=[numpy.get_include()]),
]

setup(
    name="LASSIM",
    version=__version__,
    url="https://github.com/gmariotti/lassim",
    license=__license__,
    author=__author__,
    description="The LASSIM toolbox",
    cmdclass=compiler,
    ext_modules=cythonize(extensions)
)
