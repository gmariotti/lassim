INSTALLATION GUIDE
==================

How to use the toolbox
----------------------
Before running the LASSIM toolbox is necessary to have completed the steps [Boost installation](#boost-installation)
and [PyGMO installation](#pygmo-installation), while [GSL installation](#gsl-installation) is optional for now. 
Use the files in the `examples` folder for testing the toolbox or as an example on how to format your data.

**[!]** Sometimes it is possible that Boost and/or GSL are already installed in your system. Try to build 
PyGMO against them, but if any error occurs, start considering the possibility of a local installation.

**[!]** All the installation processes assume clang as the default compiler, but it is not mandatory.

Boost installation
------------------
Download `boost_<version>.tar.gz` from [boost website](http://www.boost.org), then run the following commands:
```
tar -xvzf boost_<version>.tar.gz
cd boost_<version>
./bootstrap.sh --with-toolset=clang --prefix=path/to/install/boost-<version>
./b2 toolset=clang
./b2 install
```

Then, add the following environment variables, usually by adding them to the `.bashrc` file
```
# CUSTOM - boost
vboost="1.61.0"
export LIBRARY_PATH="$LIBRARY_PATH:path/to/install/boost-$vboost/lib"
export CPATH="$CPATH:path/to/install/boost-$vboost"
export LD_LIBRARY_PATH="path/to/install/boost-$vboost/lib:$LD_LIBRARY_PATH"
export PATH="$PATH:path/to/install/boost-$vboost/include:path/to/install/boost-$vboost/lib"
```

The version used for development is the [1.61.0](https://sourceforge.net/projects/boost/files/boost/1.61.0/boost_1_61_0.tar.gz)

GSL installation
----------------
Download `gsl_<version>.tar.gz` from [gsl website](http://ftp.acc.umu.se/mirror/gnu.org/gnu/gsl/), then run the following commands:
```
tar -xvzf gsl_<version>.tar.gz
cd gsl_<version>
export CC=clang
export CXX=clang++
./configure --prefix=path/to/install/gsl-<version>
make
make check
make install
make installcheck
```
Verify that all the test are passed.

Then, add the following environment variables, usually by adding them to the `.bashrc` file
```
# CUSTOM - gsl
vgsl="2.2.1"
export LIBRARY_PATH="$LIBRARY_PATH:path/to/install/gsl-$vgsl/lib"
export LD_LIBRARY_PATH="path/to/install/gsl-$vgsl/lib:$LD_LIBRARY_PATH"
export LD_RUN_PATH="path/to/install/gsl-$vgsl/lib:$LD_RUN_PATH"
export PATH="$PATH:path/to/install/gsl-$vgsl/include:path/to/install/gsl-$vgsl/lib"
```

The version used for development is the [2.2.1](http://ftp.acc.umu.se/mirror/gnu.org/gnu/gsl/gsl-2.2.1.tar.gz)

PyGMO installation
------------------

```
export CC=clang
export CXX=clang++

git clone https://github.com/esa/pagmo.git
cd path/to/pagmo
mkdir build
cd build
ccmake ..
```
Enable the following flags:
```
BUILD_MAIN              ON
BUILD_PYGMO             ON
CMAKE_INSTALL_PREFIX    path/to/install/pagmo
ENABLE_GSL              ON
ENABLE_TESTS            ON
INSTALL_HEADERS         ON
```
Then complete the installation with
```
make
make test
make install
python -c "from PyGMO import test; test.run_full_test_suite()"
```
Make sure to pass all the test after the call to `make test` and `python -c ...`

Then, add the following environment variables, usually by adding them to the `.bashrc` file
```
# CUSTOM - PyGMO
export CPLUS_INCLUDE_PATH="path/to/python/include/python<version>/:$CPLUS_INCLUDE_PATH"
export LD_LIBRARY_PATH="path/to/install/pagmo/lib:$LD_LIBRARY_PATH"
```

Known Issues
------------
- **[FIXED]** Before installing PyGMO on Ubuntu based distributions, is necessary to modify **line 397** of 
`pagmo/CMakeLists.txt` with the following one:  
`TARGET_LINK_LIBRARIES(main pagmo_static ${MANDATORY_LIBRARIES})`

- Seems like that versions of [SciPy > 1.17.1](http://www.scipy.org/) are missing **libstdc++.so** or have a version of it
different from **GLIBCXX_3.4.21**. If you're using [Anaconda](https://anaconda.org/), version [4.1.1](https://repo.continuum.io/archive/index.html) is the best one to
install, at least for now.