# PDI hands-on
4 simple exercice that manipulate PDI

## Environment required on the poincare machine

```bash
source /gpfslocal/pub/pdi-training/load.sh
```

## To submit the execution of the application on the poincare machine

```bash
llsubmit job_poincare
```

## Exercices
0. Getting started
  * In directory HDF5 hands-on/hdf5-1, Examine the source code, compile and run it
  * Examine the output file example.h5 with h5ls and h5dump command line tools
  * Compare this output with the output you should obtain in the solution directory

1. Modify the program to:
  * allocate and initialise a 3D array of size Nx.Ny.Nz
  * write an additional dataset containing this 3D array

2. Modify the program to write, in a new 2D dataset, a single 2D slice of the 3D array instead of the whole 3D array

3. Modify the program to write the previous 2D slice as an extension of the original 2D dataset IntArray

4. Play with chunks, groups and attributes and try the command h5ls and h5ls -v

5. Parallel multi files: all MPI ranks write their whole memory in separate file (provided in phdf5-1)

6. Serialized: each rank opens the same file (rank 0 has to create it first) and writes its data one after the other
	* Data written as separate datasets => One file with multiple datasets
	* Data written in the same dataset => One file with one single dataset

7. Parallel single file: specific HDF5 parameters given at open and write time to let MPI-IO manage the concurrent file access
