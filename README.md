# PDI hands-on

simple exercises to manipulate PDI

## Environment required on the poincare machine

Add the following line at the end of your bashrc & profile file to load the PDI library:
```bash
source /gpfslocal/pub/pdi-training-env.bash
```
then log out and in again.

Setup the compilation by detecting all dependencies (MPI, paraconf, PDI, ...) using cmake:
```bash
cmake .
```

## Ex1. Getting started

Ex1 is a simple MPI stencil code.
Examine the source code, compile it and run it.
```bash
make ex1        # compile the code
llsubmit ex1.sh # run the code
```

Play with and understand the code parameters in ex1.yml

Run the code with 3 MPI processes.

## Ex2. Now with some PDI

Ex2 is the same code as ex1 with PDI calls added.
The PDI test plugin is used to trace PDI calls.

Examine the source code, compile it and run it.
```bash
make ex2        # compile the code
llsubmit ex2.sh # run the code
```

Add the required `PDI_share` and `PDI_reclaim` calls to match the output of `ex2.out`

Notice that some share/reclaim pairs come one after the other while others are interlaced.
Is one better than the other?

## Ex3. HDF5 through PDI

Let's take the code from ex2 and make it output some HDF5 data.
No need to touch the C code here, the PDI yaml file should be enough.
We have replaced the PDI test plugin by the Decl'HDF5 plugin.

Examine the yaml, compile the code and run it.
```bash
make ex3        # compile the code
llsubmit ex3.sh # run the code
```

We need to fill 2 sections in the yaml file:
* the `metadata` section to indicate to PDI the type of the fields that are exposed,
* the `decl_hdf5` for the configuration of the Decl'HDF5 plugin

Only dsize is written as of now, let's add `psize` and `pcoord` to match the content expected described in `ex3.out`.

## Ex4. Writing some real data

We keep the same code and touch only the yaml file again.

This time:
* we will write the real 2D data contained in `main_field`,
* we will use 2 MPI processes.

Notice that we use a list to write multiple files in the decl_hdf5 section instead of a single mapping as before.

Examine the yaml, compile the code and run it.
```bash
make ex4        # compile the code
llsubmit ex4.sh # run the code
```

Unlike the other fields we manipulated until now, the type of `main_field` is not fully known, its size is dynamic.
By moving other fields in the metadata section, we can reference them from "$ expressions" in the configuration file.
This can be used to specify a dynamic size for `main_field`.

Unlike the other fields we manipulated until now, `main_field` is exposed multiple times.
In order not to overwrite it every time it is exposed, we can add a `when` condition to restrict its output.
Only write `main_field` at the second iteration (when `ii==0`).

Change the parallelism degree to 2 in height (don't forget to use 2 processes in ex4.sh) and try to match the expected content described in `ex4.out`.

## Ex5. Introducing events

In ex4, we wrote 2 pieces of data to `ex4-data*.h5`, but the file is opened and closed for each and every write.
Since Decl'HDF5 only sees the data appear one after the other, it does not keep the file open.
Since `ii` and `main_field` are shared in an interlaced way, they are both available at the same time and could be written without opening the file twice.
We have to use events for that.

Examine the yaml and source code, compile and run.
```bash
make ex5        # compile the code
llsubmit ex5.sh # run the code
```

Add a `PDI_event` call to the code when both `ii` and `main_field` are available.
With the test plugin, check that the event is indeed triggered at the expected time as described in `ex5-trace.out`.

Use the `on_event` mechanism to trigger the write of `ii` and `main_field`.
This mechanism can be combined with a `when` directive, in that case the write is only executed when both mechanisms agree.

Also notice the extended syntax that make it possible to write data to a dataset with a name different from the data in PDI.
Use this mechanism to write main_field at iterations 1 and 2, in two distinct groups.
Match the content as expected in `ex5-hdf5.out`.

## Ex6. Simplifying the code

As you can notice, the PDI code is quite redundant.
In this exercise, we will use `PDI_expose` and `PDI_transaction_*` to simplify the code while keeping the exact same behaviour.

Examine the source code, compile it and run it.
```bash
make ex6        # compile the code
llsubmit ex6.sh # run the code
```

There are lots of matched `PDI_share`/`PDI_reclaim` in the code.
Replace these by `PDI_expose` that is the exact equivalent of a `PDI_share` followed by a matching `PDI_reclaim`.

This replacement is not possible for interlaced `PDI_share`/`PDI_reclaim` with events in the middle.
This case is however handled by `PDI_transaction_*`, enclosing `PDI_expose` inside `PDI_transaction_begin`/`PDI_transaction_end` delays the reclaims until the end of the transaction.
It also triggers an event when all the share of the transaction are done.
Replace the remaining `PDI_share`/`PDI_reclaim` by `PDI_expose`s and `PDI_transaction_*`.

Ensure that your code keeps the exact same behaviour by comparing its trace to `ex6.out`

## Ex7. writing a selection

In this exercise, we will only write a selection of the data to the HDF5 file.

Examine the yaml, compile the code and run it.
```bash
make ex7        # compile the code
llsubmit ex7.sh # run the code
```

As you can notice, we now independantly describe the dataset in the file.
We also use two directives to specify a selection from the data to write and a selection in the dataset where to write.

Restrict the selection to the second line from the data and write it to a one-dimensional dataset in file.
Match the expected output described in `ex7.out`.

You can also add dimensions, write the 2D array excluding ghosts as a slab of a 3D dataset including a dimension for the time-iteration.
Write iterations 1 to 3 inclusive into dimensions 0 to 2.
Match the expected output described in `ex7-bis.out`.

## Ex8. going parallel

Running the current code in parallel should already work and yield one file per process containing the local data block.
In this execise we will write one single file with parallel HDF5 whose content should be independant from the number of processes used.


Examine the yaml, compile the code and run it.
```bash
make ex8        # compile the code
llsubmit ex8.sh # run the code
```

By uncommenting the communicator directive (only world supported now), we switch to parallel I/O.
* Change the file name so all processes open the same file.
* Change the dataset dimension to take the full parallel size into account.
* Ensure the dataset selection of each process does not overlap with the others.
* Try to match the output from `ex8.out` that should be independant from the number of processes used.

## What next ?

You can experiment with other plugins
* FTI: efficient fault tolerance support
* user-code: run and compose your own functions on the data exposed through PDI

Take a look at the examples in the PDI repository:
`https://gitlab.maisondelasimulation.fr/jbigot/pdi/tree/v0.1/example`
