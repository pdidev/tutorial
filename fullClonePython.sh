#!/bin/bash

git clone git@github.com:pdidev/pdi.git
cd pdi
git clone git@github.com:pdidev/tutorial.git -b new_2024
mkdir build
cd build
cmake ..
mkdir ../../local
cmake -DBUILD_PYCALL_PLUGIN=ON -DBUILD_PYTHON=ON -DUSE_HDF5="EMBEDDED" -DUSE_NetCDF="EMBEDDED" ..
make -j8
source ./staging/share/pdi/env.sh
cd ../tutorial
cmake .
cp ./solutions/ex10.yml ./ex10.yml
make ex10
mpirun -np 4 ./ex10