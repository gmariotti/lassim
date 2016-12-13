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

How to install and use the toolbox
----------------------------------
Before using the the toolbox, be sure to satisfy all the requirements in the [Development environment and requirements](#development-environment-and-requirements). After you have done that, run the following command from a terminal:
```
git clone https://github.com/gmariotti/lassim.git
cd lassim
./scripts/install.sh
```

For the core optimization, the command is:
```
python lassim_core.py <terminal-options>
```
while for the list of terminal options availables use the command:

`python lassim_core.py -h` or `python lassim_core.py --help`

Development environment and requirements
----------------------------------------
The current environment on which the toolbox is developed and tested is:

- [Fedora 25 Workstation](https://getfedora.org/)
- [PyCharm 2016.x](https://www.jetbrains.com/pycharm/)
- [Anaconda 4.1.1](https://anaconda.org/) with Python 3.5.2
- [Boost 1.61.0](http://www.boost.org)
- [GSL 2.2.1](http://ftp.acc.umu.se/mirror/gnu.org/gnu/gsl/)
- [clang 3.8](http://clang.llvm.org/)

but is going to be tested and used mainly on the [NSC](https://www.nsc.liu.se) system available at the [Linköping University](http://liu.se/?l=en).

Instead, the list of **mandatory** dependencies is:

- [PyGMO 1.1.7](http://esa.github.io/pygmo/index.html)
- [NumPy 1.11.1/SciPy 0.17.1](http://www.scipy.org/)
- [pandas 0.18.1](http://pandas.pydata.org/)
- [Cython >= 0.24.0](http://cython.org/)
- [sortedcontainers >= 1.5.3](http://www.grantjenks.com/docs/sortedcontainers/)

Except for [sortedcontainers](http://www.grantjenks.com/docs/sortedcontainers/), all of them are already present in [Anaconda 4.1.1](https://anaconda.org/).

For tips on how to install [PyGMO](http://esa.github.io/pygmo/index.html), look at [INSTALL](INSTALL.md) file.

**[!]** clang compiler seems to be the one that gives less problems during the compilation process, 
but, even if not tested, there shouldn't be any issue with the gcc compiler too.

What's next?
------------

- Analysis of peripherals genes against an existing core system.
- Possibility of installing `source/core` as a Python module.
- Configuration file for setting terminal parameters.
- New kind of base implementation for the optimization process, in order to use different algorithm 
in different ways.
- New formats for input data.
- Improvements on tests, documentation and code quality.
- A Gitter channel.

[Here](https://python3statement.github.io/) you can find one of the reasons why the support for Python 2.7 is highly improbable.

Current Branches
----------------

The `master` branch, usually, contains working code, tested on different environments. Check `releases` to see the 
latest stable version of the toolbox.

The `development` branch, instead, contains unstable, untested code, with future features and bug fixes, should not 
be used unless you want to help with the development. 

References
----------
> **The generalized island model**, Izzo Dario and Ruci&#324;ski Marek and Biscani Francesco, Parallel Architectures and Bioinspired Algorithms, 151--169, 2012, Springer 
