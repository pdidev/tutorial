This tutorial will be done the version 1.*.** of PDI

# installation

Create a directory for this tutorial

## spack install or docker:

## install from source:

prerequies:
- C/C++ compiler (tested with gcc and clang)
- cmake
- mpi (tested with openmpi and mpich)
- A version of python 3 with numpy, matplotlib and pybind11 $^{*}$
- hdf5 $^{*}$
- deisa $^{*}$
- The other prerequies can be obtained at the compilation of pdi.

### how to set pyton environement with venv


```bash
python3 -m venv env_python_tuto_pdi
source env_python_tutu_pdi/bin/activate
python3 -m pip install --upgrade pip 
python3 -m pip install numpy matplotlib 
```

### how to install pdi

```bash
git clone https://github.com/pdidev/pdi
git switch v1.*.*
```

```bash
cd pdi
mkdir install
mkdir build
cd build
```

```bash
cmake \
-DCMAKE_INSTALL_PREFIX=../install
-DBUILD_MPI_PLUGIN \
-DBUILD_DECL_HDF5_PLUGIN=ON -DBUILD_HDF5_PARALLEL=ON -DUSE_HDF5=EMBEDDED \
-DBUILD_PYTHON=ON -DBUILD_PYCALL=EMBEDDED -DUSE_pybind11=EMBEDDED \
-DBUILD_USER_CODE_PLUGIN=ON \
-DUSE_spdlog=EMBEDDED \
-DUSE_yaml=EMBEDDED \
-DUSE_paraconf=EMBEDDED \
..
```

source the environement of pdi:
* with a bash script
```bash
cd ../..
source ./pdi/install/share/pdi/env.bash
```
* with a zsh script (default script on MAC OSX)
```bash
cd ../..
source ./pdi/install/share/pdi/env.zsh
```

An installation script of pdi, 

### checking your environnement

A script to check your environnement is given here.

```bash
A completer.
```
