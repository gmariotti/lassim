LASSIM Toolbox
==============

About LASSIM and the LASSIM toolbox
-----------------------------------

Recent and ongoing improvements in measurements technologies have given the possibility 
to obtain systems wide omics data of several biological processes. However, the analysis of 
those data has to date been restricted to crude, statistical tools with important biological 
mechanisms, e.g. feedback loops, being overlooked. The omitting of such high influence details 
in a large scale network remains a major problem in today’s omics based environment and is a 
key aspect of truly understanding any complex disease. Therefore, we herein present the 
**LASSIM** (**LA**rge **S**cale **SIM**ulation based network identification) toolbox, which revolves around the 
expansion of a well determined mechanistic ODE-model into the entire system.

With this toolbox is possible to run a default implementation of `lassim`, but also to
extend and improve its behaviour by creating new optimization algorithms, using a different 
system of odes, different types of integrators, and more.

All the optimization algorithms currently available are implemented by using [PyGMO](http://esa.github.io/pygmo/index.html) but there 
are no limitations on how the algorithms should be implemented, what it's important is to respect
the signatures of the classes that are part of the module `source/core`

Important 
---------

This is an alpha version, the probability of bugs is really high, a lot of tests are still missing, and 
everything is still subject to modifications and refactoring. But still, it has been decided to make it
publicly available in order to show more or less how the toolbox will work, to accept feedback and
to give the possibility to whoever is interested in the project to help its development.

Installation
------------

The toolbox has been developed on Python 3.5, using the environment offered by [Anaconda 4.1.1](https://anaconda.org/).

The list of **mandatory** dependencies is:

- [PyGMO 1.1.7](http://esa.github.io/pygmo/index.html)
- [NumPy 1.11.1/SciPy 1.17.1](http://www.scipy.org/)
- [pandas 1.18.1](http://pandas.pydata.org/)
- [sortedcontainers 1.5.3](http://www.grantjenks.com/docs/sortedcontainers/)

For some tips on how to install PyGMO, look at [Suggestions for PyGMO installation](#Suggestions-for-PyGMO-installation).

Environment used for development
--------------------------------

The current environment on which the toolbox is developed and tested is:

- [Linux Mint 18 Cinnamon](https://linuxmint.com/)
- [PyCharm Community 2016.2](https://www.jetbrains.com/pycharm/)
- [Anaconda 4.1.1](https://anaconda.org/)

but it will be further tested on the [NSC](https://www.nsc.liu.se) system available at the [Linköping University](http://liu.se/?l=en).

What's next?
------------

- Implementation of `CoreWithKnocksProblem` for handling the core creation problem in case knocks data are available.
- Possibility of installing `source/core` as a Python package.
- Implementation of Basin Hopping algorithm from [PyGMO](http://esa.github.io/pygmo/index.html)
- Improvements on tests, documentation and code quality.

[Here](https://python3statement.github.io/) you can find one of the reasons why the support for Python 2.7 is highly improbable.

Suggestions for PyGMO installation
----------------------------------

The current version on [PyGMO](http://esa.github.io/pygmo/index.html) used is the 1.1.7 available on the master branch. It has been 
performed a vanilla installation on local, and not as a root user. The options `BUILD_MAIN` and 
`BUILD_PYGMO` where turned on, the version 1.61.0 of [Boost C++ Libraries](http://www.boost.org/) has been used, the 
compilation has been done with [clang 3.8](http://clang.llvm.org/).

The following environment variables have been modified in order to complete the compilation and 
running the program:

- COMPILER_PATH="$COMPILER_PATH:*boost-dir-path*"
- LIBRARY_PATH="$LIBRARY_PATH:*boost-dir-path*/lib"
- LD_LIBRARY_PATH="*boost-dir-path*/lib:/*pagmo-dir-path*/lib:$LD_LIBRARY_PATH"
- CPLUS_INCLUDE_PATH="*anaconda3-dir-path*/include/python3.5m/:$CPLUS_INCLUDE_PATH"
- PATH="$PATH:*boost-dir-path*/include:*boost-dir-path*/lib"

**[for Ubuntu users]** for completing the installation of [PyGMO](http://esa.github.io/pygmo/index.html) on Ubuntu based systems, is necessary
to modify line 397 of the `pagmo/CMakeLists.txt` file has shown below.

`TARGET_LINK_LIBRARIES(main pagmo_static ${MANDATORY_LIBRARIES})`

Known Issues
------------
- Seems like that versions of [SciPy](http://www.scipy.org/) greater than the one in [Installation](#Installation) are missing **libstdc++.so** or 
have a version of it different from **GLIBCXX_3.4.21**. If you're using [Anaconda](https://anaconda.org/), version [4.1.1](https://repo.continuum.io/archive/index.html) is the best one 
to install, at least for now.