# Hands-on tutorial {#Hands_on}

In this tutorial, you will build a PDI-enabled application step-by-step from a
PDI-free base.
You will end-up building the C version of the
\ref PDI_example "example provided with PDI" for the the
\ref trace_plugin "Trace", \ref Decl_HDF5_plugin "Decl'HDF5", and
\ref pycall_plugin "Pycall" plugins.
Additional [examples are available for the other plugins](https://gitlab.maisondelasimulation.fr/pdidev/pdi/-/tree/master/example).


## Setup

\attention
To run this hands-on tutorial, you first need to \ref Installation "install PDI"
and setup your environment.

### PDI installation

\ref Installation "PDI installation" is documented in a
\ref Installation "dedicated page".


### Hands-on tutorial setup

Once %PDI is installed, you can proceed with getting the sources for the
hands-on tutorial from [github](https://github.com/pdidev/tutorial):
```bash
git clone https://github.com/pdidev/tutorial.git
cd tutorial
```


### Compilation

Before compilation, configure the tutorial by detecting all dependencies:
```bash
pdirun cmake .
```

\attention
If you installed PDI in a standard path, the `pdirun` prefix is never required.

Once you have correctly modified each exercise according to instructions, you
can compile it by running:
```bash
pdirun make ex?
```
Where `?` is the number of the exercise.


### Execution

You can run each exercise with the following command:
```bash
pdirun mpirun -n 4 ./ex?
```
Where `?` is the number of the exercise and 4 represents the number of MPI
processes to use.

To store the logs for later comparison, you can use the following command (for
example for ex2.):
```bash
pdirun mpirun -n 1 ./ex2 | tee ex2.result.log
```

Now you're ready to work, **good luck**!


## PDI-free code

### Ex1. Getting started

Ex1. implements a simple heat equation solver using an explicit forward finite
difference scheme parallelized with MPI.
The code uses a block domain decomposition where each process holds a 2D block
of data.

![Data domain decomposition in the example](heat_global_matrix.jpg)

Locally, each process holds its local block of data with one additional element
on each side for ghost zones.

![Data domain decomposition in the example](heat_local_matrix.jpg)

In the following exercises however, %PDI will only be used to decouple I/O
operations.
There is no need to fully dive in the core of the solver described in the
\ref heat_algorithm "PDI example algorithm" and implemented in the `iter` and
`exchange` functions.

The specification tree in the `.yml` files and the `main` function are the
locations where all the I/O-related aspects will be handled and the only ones
you will actually need to fully understand or modify.

* Examine the source code, compile it and run it.
  There is no input/output operations in the code yet, so you can not see any
  result.

This example gets its configuration from a file in the \ref YAML "YAML format":
`ex1.yml` file.
If you're not familiar with YAML, please have a look at our quick
\ref YAML "YAML format documentation" to understand it.
The example uses the [paraconf library](https://github.com/pdidev/paraconf) to
read this file.

* Play with and understand the code parameters in `ex1.yml`.

* Set values in `ex1.yml` to be able to run the code with 4 MPI processes.

```bash
srun -n 4 ./ex1
```


## PDI core & trace plugin

### Ex2. Now with some PDI

Ex2. is the same code as that of ex1. with %PDI calls added in `main` function.
In our YAML file (`ex2.yml`), a new sub-tree has been added under the `pdi` key.
This sub-tree is the %PDI specification tree passed to %PDI at initialization.
Here, the %PDI \ref trace_plugin "Trace plugin" is used to trace %PDI calls.

* Examine the source code, compile it and run it.

* Add the required `::PDI_share` and `::PDI_reclaim` calls to match the output
  of `ex2.log` file (only the lines matching `[Trace-plugin]` have been kept).
  You only need to change the `ex2.c` file. You can easily check if the files
  are the same by running the command:
```bash
  diff ex2.log <(grep Trace-plugin ex2.result.log)
```

\attention
Notice that some share/reclaim pairs come one after the other while others are
interlaced.
Is one better than the other?
If you do not know the answer to this question, just wait until Ex5. :)


## Decl'HDF5 plugin

In exercise 3 to exercise 9 included, we present the \ref Decl_HDF5_plugin "Decl'HDF5 plugin" (`decl_hdf5`).
We will introduce some keyword (`when`, `datasets`, ...) in the sub-tree of `decl_hdf5` in configuration YAML file.

All keywords are defined in the last section **full configuration example** of \ref Decl_HDF5_plugin "Decl'HDF5 plugin".

### Ex3. HDF5 through PDI

In this exercise, the C code is the same as in ex2. No need to touch the C code here, modification of the YAML file (`ex3.yml`)
should be enough.

* Examine the YAML file, compile the code and run it.

The \ref Decl_HDF5_plugin "Decl'HDF5 plugin" (`decl_hdf5`) is added in the specification tree.
In its configuration, the `dsize` variable is defined as a metadata for %PDI.

* Write the `psize` and `pcoord` variables in addition to `dsize` in a file `ex3.h5` with one MPI process. 
To achieve this result, you will need to fill 2 sections in the YAML file:

  1. The `data` section to indicate to %PDI the \ref datatype_node "type" of the fields that are exposed.

  2. The `decl_hdf5` section for the configuration of the \ref Decl_HDF5_plugin "Decl'HDF5 plugin".

* Use the `h5dump` command to see the content of your HDF5 output file in the same format as the h5dump file `ex3.h5dump`. You can easily check if the files are the same by running:
```bash
  diff ex3.h5dump <(h5dump ex3*.h5)
```
To see your `h5` file in readable file format, you can check the section [Comparison with the `h5dump` command](#h5comparison).

\warning
If you relaunch the executable, remember to delete your old `ex3.h5` file before, otherwise the data will not be changed.

\warning
With more than one MPI rank is used, we write to the same location in the file independently of the MPI rank. 
For this reason, this exercise will fail. The next exercise solves this issue.

### Ex4. Writing some real data

In this exercise each MPI process will write its local 2D array block contained
in the `main_field` variable to a separate HDF5 file.
Once again, this can be done by modifying the YAML file only, no need to touch
the C file.

* Examine the YAML file, compile the code and run it.

\note Notice that in the YAML file `ex4.yml`, a list was used in the `decl_hdf5` section with
multiple write blocks instead of a single one as before in order to write to
multiple files.

\note Notice that we have moved fields (`dsize`, `psize` and `pcoord`) in the `metadata` section.
```yaml
pdi:
  metadata: # small values for which PDI keeps a copy
    #*** add ii as metadata
    #...
    dsize: { type: array, subtype: int, size: 2 }
```
You can reference them from dynamic "$-expressions" in the configuration file.

\remark Also notice that this example now runs in parallel with 4 processes.
To ensure we do not write to the same file, we need  to specify the file name using "$-expressions" for the different process rank. 

Unlike the other fields manipulated until now, the type of `main_field` is not fully known, its size is dynamic.
Therefore, we need to define the size in YAML file for %PDI using "$-expressions".

* Describe the temperature data on the current iteration by using a $-expression to specify the size of `main_field` in `data` section.

Unlike the other fields manipulated until now, `main_field` is exposed multiple times along execution.
In order not to overwrite it every time it is exposed, you propose to write one file per rank only at the first iteration (`ii=1`) with the directive `when`.

* Add the iteration loop `ii` as a metadata.
* Write the curent temperature field in one file per process at first iteration.

You should be able to match the expected output described in `ex4.h5dump`. You can easily check if the files are the same by running:
```bash
  diff ex4.h5dump <(h5dump ex4-data-*.h5)
```
To see your `h5` file in readable file format, you can check the section [Comparison with the `h5dump` command](#h5comparison).

\note A definition of `metadata` and `data` can be:\n  
- `metadata`: small values for which PDI keeps a copy. These value can be referenced by using "$-expressions" in the configuration YAML file.
- `data`    : values for which PDI does not keep a copy.

### Ex5. Introducing events and group of dataset

This exercise is done in sequential to facilitate the comparison between logs.

#### Ex 5.1 PDI event and on_event

In ex4, two variables were written to `ex4-data*.h5`, but the files were opened
and closed for each and every write.

Since Decl'HDF5 only sees the data appear one after the other, it does not keep
the file open. Since `ii` and `main_field` are shared in an interlaced way, they are both
available to %PDI at the same time and could be written without opening the file
twice.
You have to use events for that, you will modify both the C and YAML file in this exercise.

* Examine the YAML file and source code.
* In the C file, add a %PDI event named `loop` when both `ii` and
  `main_field` are shared.

  With the \ref trace_plugin "Trace plugin", check that the event is indeed
  triggered at the expected time as described in `ex5.log` (only the lines
  matching `[Trace-plugin]` have been kept). Using the previous section [Execution with storage of the log](#execution-with-storage-of-the-log),
  run  this exercise in saving the output log in the `ex5.result.log`. After that you can easily check if the files are the same by running:
```bash
  diff ex5.log <(grep Trace-plugin ex5.result.log)
```
* In the YAML file, use the `on_event` mechanism to trigger the write of `ii` and `main_field` 
  for event `loop` only. This mechanism can be combined with a `when` directive, in that case the write is only executed when both mechanisms agree.
* Add the `when` directive to write only at iteration 1 and 2. Use the symbol `&` which corresponds to the logical operation `and`.

#### Ex 5.2 group of dataset
In ex4, the name of the datasets of `.h5` file are `ii` and `main_field`(see ex4.h5dump).
Using the keyword `dataset`, it is possible to have a different name from the %PDI variable name.

The name of the dataset is given after the definition of the data 
```yaml
       write:
          ii: # name of the PDI data to write
            dataset: 'new_name' 
```
Using this mechanism, it is possible to define a group object of hdf5 see https://support.hdfgroup.org/documentation/hdf5/latest/_h5_g__u_g.html.
If you want to add a dataset `my_data` in the sub-group `groupA` of the group `my_group`, the name of the dataset will be:
```yaml
dataset: 'my_group/groupA/my_data'.
```
where the symbol "/" is used to separate groups in path.

* Change the YAML file to write `main_field` and `ii` at iterations 1 and 2, in two distinct groups `iter1` and `iter2`.

  To match the expected output described in `ex5.h5dump`. You can easily check if the files are the same by running:
```bash
  diff ex5.h5dump <(h5dump ex5-data-*.h5)
```
  To see your `h5` file in readable file format, you can check the section [Comparison with the `h5dump` command](#h5comparison).


### Ex6. Simplifying the code

As you can notice, the %PDI code is quite redundant.
In this exercise, you will use `::PDI_expose` and `::PDI_multi_expose` to
simplify the code while keeping the exact same behaviour.
For once, there is no need to modify the YAML file here, you only need to modify
the C file in this exercise.

* Examine the source code, compile it and run it.

There are lots of matched `::PDI_share`/`::PDI_reclaim` in the code.

* Replace these by `::PDI_expose` that is the exact equivalent of a
  `::PDI_share` followed by a matching `::PDI_reclaim`.

This replacement is not possible for interlaced `::PDI_share`/`::PDI_reclaim`
with events in the middle.
This case is however handled by `::PDI_multi_expose` call that exposes all data,
then triggers an event and finally does all the reclaim in reverse order.

* Replace the remaining `::PDI_share`/`::PDI_reclaim` by `::PDI_expose`s and
  `::PDI_multi_expose`s and ensure that your code keeps the exact same behaviour
  by comparing its trace to `ex6.log` (only the lines matching `[Trace-plugin]`
  have been kept). You can easily check if the files are the same by running:
```bash
  diff ex6.log <(grep Trace-plugin ex6.result.log)
```


### Ex7. Writing a selection

In this exercise, you will only write a selection of the 2D array in memory
excluding ghosts to the HDF5 file.
Once again, you only need to modify the YAML file in this exercise, no need to
touch the C file.

* Examine the YAML file and compile the code.

As you can notice, now the dataset is independently described in the file.

* Restrict the selection to the non-ghost part of the array in memory (excluding
  one element on each side).
  You should be able to match the expected output described in `ex7.h5dump`.
  You can easily check if the files are the same by running:
```bash
  diff ex7.h5dump <(h5dump ex7*.h5)
```

You can achieve this by using the `memory_selection` directive that specifies
the selection of data from memory to write.

![graphical representation](PDI_hdf5_selection.jpg)


### Ex8. Selecting on the dataset size

In this exercise, you will once again change the YAML file to handle a selection
in the dataset in addition to the selection in memory from the previous
exercise.
You will write the 2D array from the previous exercise as a slice of 3D dataset
including a dimension for time.
Once again, you only need to modify the YAML file in this exercise, no need to
touch the C file.

* Examine the YAML file and compile the code.

Notice how the dataset is now extended with an additional dimension for three
time-steps.

* Write the 2D selection from `main_field` at iterations 1 to 3 inclusive into
  slices at coordinate 0 to 2 of first dimension of the 3D dataset.
  Match the expected output described in `ex8.h5dump`. You can easily check if
  the files are the same by running:
```bash
  diff ex8.h5dump <(h5dump ex8*.h5)
```

You can achieve this by using the `dataset_selection` directive that specifies
the selection where to write in the file dataset.

![graphical representation](PDI_hdf5_selection_advanced.jpg)


## parallel Decl'HDF5

### Ex9. Going parallel

Running the code from the previous exercises in parallel should already work and
yield one file per process containing the local data block.
In this exercise you will write one single file with parallel HDF5 whose content
should be independent from the number of processes used.
Once again, you only need to modify the YAML file in this exercise, no need to
touch the C file.

* Examine the YAML file and compile the code.

The `mpi` plugin was loaded to make sharing MPI communicators possible.

* Uncomment the `communicator` directive of the
  \ref Decl_HDF5_plugin "Decl'HDF5 plugin" to switch to parallel I/O and change
  the file name so that all processes access the same file.

* Set the size of the dataset to take the global (parallel) array size into
  account.
  You will need to multiply the local size by the number of processes in each
  dimension (use `psize`).

* Ensure the dataset selection of each process does not overlap with the others.
  You will need to make a selection in the dataset that depends on the global
  coordinate of the local data block (use `pcoord`).

Match the output from `ex9.h5dump`, that should be independent from the number
of processes used. You can easily check if the files are the same by running:
```bash
  diff ex9.h5dump <(h5dump ex9*.h5)
```

![graphical representation of the parallel I/O](PDI_hdf5_parallel.jpg)


## Pycall

### Ex10. Post-processing the data in python

In this exercise, you will once again modify the YAML file only and use python
to post-process the data in situ before writing it to HDF5.
Here, you will write the square root of the raw data to HDF5 instead of the
data itself.

* Examine the YAML file and compile the code.

Notice that the Decl'HDF5 configuration was simplified, no memory selection is
applied, the when condition disappeared.
The dataset name is however explicitly specified now because it does not match
the %PDI variable name anymore, you will instead write a new variable exposed
from python.

The `pycall` section has been added to load the 
\ref pycall_plugin "Pycall plugin".
It executes the provided code when the "loop" event is triggered.
The `with` section specifies the variables (parameters) to pass to Python as a
set of "$-expressions".
The provided code again exposes its result to %PDI and multiple blocks can be
chained this way.

* Add the missing parameter to the `with` block to let the Python code process
  the data exposed in `main_field`.

* Modify the Decl'HDF5 configuration to write the new data exposed from Python.

* Match the output from `ex10.h5dump`. You can easily check if the files are the
  same by running:
```bash
  diff ex10.h5dump <(h5dump ex10*.h5)
```

\attention
In a more realistic setup, one would typically not write much code in the YAML
file directly, but would instead call functions specified in a `.py` file on
the side.

## What next ?

In this tutorial, you used the C API of %PDI and from YAML, you used the 
\ref trace_plugin "Trace", \ref Decl_HDF5_plugin "Decl'HDF5", and
\ref pycall_plugin "Pycall" plugins.

If you want to try PDI from another language (Fortran, python, ...) or if you
want to experiment with other \ref Plugins "PDI plugins", have a look at the
[examples provided with PDI](https://gitlab.maisondelasimulation.fr/pdidev/pdi/-/tree/master/example).
