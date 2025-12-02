# NumpEX tutorial: managing I/O with PDI

# Join the Zoom Meeting

Zoom link: [https://cnrs.zoom.us/j/94401006871?pwd=bN7EnXdz7gMTPEexTkjvG5FgqDqgrh.1](https://cnrs.zoom.us/j/94401006871?pwd=bN7EnXdz7gMTPEexTkjvG5FgqDqgrh.1)

# How to connect to Grid’5000

## Configure your access to Grid’5000

Please check the Getting Started section of the Grid’5000 website:   
[https://www.grid5000.fr/w/Getting\_Started\#Connect\_to\_a\_Grid'5000\_access\_machine](https://www.grid5000.fr/w/Getting_Started#Connect_to_a_Grid'5000_access_machine)

**TL;DR**: your local .ssh/config should include the following lines:

| Host g5k  User \<your\_username\>  HostName access.grid5000.fr  ForwardAgent no Host \*.g5k  User \<your\_username\>  ProxyCommand ssh g5k \-W "$(basename %h .g5k):%p"  ForwardAgent no |
| :---- |

To check if your configuration works, you should be able to connect to the frontal node of the Grenoble site using the following command: 

| ssh grenoble.g5k |
| :---- |

Note that, if correctly configured, no password is requested.

## 

## Connect to a dedicated node

The following command will connect to an exclusive compute node on the dahu partition on Grid’5000 in Grenoble.

| oarsub \--project lab-2025-mdls-numpex-pdi \-t allowed=special \-I \-p dahu \-l host=1 |
| :---- |

This command will spawn a shell on one of the nodes of the dahu partition (eg, dahu-20).

Some useful commands regarding your node allocation:

| oarsub \<options\> | To reserve the necessary resources, and create a job |
| :---- | :---- |
| oarstat | To check which jobs are currently running, and what are their IDs |
| oardel \<jobID\> | To delete a job using its ID |

#### 

#### Tips for VSCode users:

Using this interactive shell, you may connect to the host in VSCode.  
In VSCode, "Connect to host" (Ctrl+Shift+P), then type the address of the allocated node (eg, dahu-20).

| dahu-20.grenoble.g5k |
| :---- |

# Prepare the tutorial material

Get the sources from GitHub and set up the environment:

| git clone \-b numpex https://github.com/pdidev/tutorial.git cd tutorial && source ./spack\_env/bootstrap\_env.sh |
| :---- |

You may test that your environment is properly set up using the dedicated script:

| ./environment\_check\_script \[...\] \[0\] SUCCESS \[1\] SUCCESS \[2\] SUCCESS \[3\] SUCCESS |
| :---- |

# Information about PDI

## API used in this tutorial

| PDI\_status\_t PDI\_init (PC\_tree\_t conf) PDI\_status\_t PDI\_finalize (PC\_tree\_t conf) PDI\_status\_t PDI\_share (const char \*name, const void \*data, PDI\_inout\_t access) PDI\_status\_t PDI\_reclaim (const char \*name)  PDI\_status\_t PDI\_expose (const char \*name, const void \*data,                           PDI\_inout\_t access) PDI\_status\_t PDI\_multi\_expose (const char \*event\_name, const char \*name,                                          const void \*data, PDI\_inout\_t access, …) PDI\_status\_t PDI\_access (const char \*name, void \*\*data, PDI\_inout\_t access) PDI\_status\_t PDI\_release (const char \*name) |
| :---- |

## PDI official webpage: [https://pdi.dev](https://pdi.dev)

## PDI official GitHub repo: [https://github.com/pdidev/pdi/](https://github.com/pdidev/pdi/)

## PDI Slack channel:[https://pdidev.slack.com/](https://pdidev.slack.com/)

## 

## 

## 

## 

## 

## 

## 

## 

## 

## Acknowledge: 

## As part of the "France 2030" initiative, this work has benefited from a State grant managed by the French National Research Agency (Agence Nationale de la Recherche) attributed to the Exa-DoST project of the NumPEx PEPR program, reference: ANR-22-EXNU-0004. 

## Part of the research presented here has received funding from the Horizon 2020 (H2020) funding framework under grant/award number: 676629 (EoCoE) and 824158 (EoCoE-II). The present publication reflects only the authors views. The European Commission is not liable for any use that might be made of the information contained therein.

# **PDI HANDS-ON**

1. The main program simulates two-dimensional heat diffusion in a square domain with two heat sources, using periodic boundary conditions.  
* Variables used in the main program main.c:  
  * int dsize\[2\]:  size of the local data as \[HEIGHT, WIDTH\], including the number of ghost layers  
  * int psize\[2\]: 2D size of the process grid as \[HEIGHT, WIDTH\]  
  * double \*\*cur: local data, of size \[dsize\[0\],dsize\[1\]\], representing the temperature  
* config.yml  
  * This file is used to set the simulation parameters.

| PC\_tree\_t conf \= PC\_parse\_path("config.yml"); |
| :---- |

    

  * We will also use this file to configure PDI.  
  * The parameter is passed to the simulation using:

    

| long longval; PC\_int(PC\_get(conf, ".parallelism.height"), \&longval); psize\[0\] \= longval; |
| :---- |

    

  * Compile and run the test using:

    

| cmake . make mpirun \-np 4 ./main |
| :---- |

2. ### \[BEGIN\] Instrument the simulation with PDI

   * Include the PDI header file \<pdi.h\> and initialize the PDI environment with 

     

| PDI\_init(PC\_get(conf, ".pdi")); PDI\_finalize(); |
| :---- |

     

   * Add a PDI section in config.yml  
     

| pdi: |
| :---- |

     

   * Modify the CMakeLists.txt to link the executable with PDI

     

| find\_package(PDI 1.9.0 REQUIRED COMPONENTS C) target\_link\_libraries(main m MPI::MPI\_C paraconf::paraconf                                 PDI::pdi) |
| :---- |

     

   * You should obtain the output as:  
     	

| \[PDI\] \*\*\* warning: Data is not defined in specification tree \[PDI\] \*\*\* info: Initialization successful \[PDI\] \*\*\* warning: Data is not defined in specification tree \[PDI\] \*\*\* info: Initialization successful \[PDI\] \*\*\* warning: Data is not defined in specification tree \[PDI\] \*\*\* info: Initialization successful \[PDI\] \*\*\* warning: Data is not defined in specification tree \[PDI\] \*\*\* info: Initialization successful \[PDI\] \*\*\* info: Finalization \[PDI\] \*\*\* info: Finalization \[PDI\] \*\*\* info: Finalization \[PDI\] \*\*\* info: Finalization \[1\] SUCCESS \[3\] SUCCESS  \[0\] SUCCESS \[2\] SUCCESS |
| :---- |

     

   * The warning states that no data definition can be found for PDI's configuration. We shall add some data to PDI in the next step.

3. ### \[TRACE\] Use the trace plugin to observe the data movement in the PDI data\_store.

   * Use PDI\_share and PDI\_reclaim to handle buffers with PDI.

     

| PDI\_share("local\_size", dsize, PDI\_OUT);PDI\_reclaim("local\_size"); |
| :---- |

     

   * Share before the temporal loop, the variable dsize to PDI with the name  "local\_size", and set it as PDI metadata:

     

| metadata:  local\_size: {type: array, subtype: int, size: 2} |
| :---- |

     

   * Share at the beginning of each iteration, and at the end of the temporal loop, the variable ii with the name "iteration", and cur with the name "temp". Set temp as PDI data:  
     

| data:  temp: {type: array, subtype: double,           size: \['$local\_size\[0\]', '$local\_size\[1\]'\]} |
| :---- |

   * Use the trace plugin:

| plugins:   trace:    logging: {pattern: '\[PDI\]\[%n-plugin\] \*\*\* %l: %v' } |
| :---- |

     	

   * Limit the total iterations to 3

     

| for (; ii \< 3; \++ii) { |
| :---- |

     

   * and set use 1 process MPI

     

| parallelism: { height: 1, width: 1 } |
| :---- |

     

   * Run the test and compare the output with the reference "trace\_reference.txt"  
   * Try with PDI\_expose and PDI\_multi\_expose

| PDI\_expose("local\_size",             dsize,             PDI\_OUT); | PDI\_share("local\_size",             dsize,            PDI\_OUT); PDI\_reclaim("local\_size"); |
| :---- | :---- |
| PDI\_multi\_expose("loop",                   "iteration",                  \&ii,                   PDI\_OUT,                   "temp",                   cur,                   PDI\_OUT,                  NULL); | PDI\_share("iteration",            \&ii,            PDI\_OUT); PDI\_share("temp",            cur,            PDI\_OUT); PDI\_event("loop"); PDI\_reclaim("temp"); PDI\_reclaim("local\_size"); |

4. ### \[PYCALL\] Use Pycall to generate partial images of the simulation.

   * With variables properly shared with PDI, we can start using PDI plugins for various purposes.  
   * Let's begin with the Pycall plugin to code Python scripts using matplotlib.  
   * You need to share the variable pcoord with PDI to set up the output image name. It is already declared in the config.yml as metadata.  
   * Several options are available to call the Python script. We will use the on\_event trigger. You can then use the PDI\_multi\_expose API to share data and trigger an event.  
     

| PDI\_multi\_expose("loop", "iteration", \&ii, PDI\_OUT,                          "temp", cur, PDI\_OUT,                           NULL); |
| :---- |

     

| pycall:   on\_event:     loop:       with: \# insert here your list of arguments       exec: |         … \# insert your Python script here |
| :---- |

     

* When passing arguments from PDI to Python, you can use:


| with: { iter\_id: $iteration} |
| :---- |


  where py\_iter, whose value is defined by iteration, can be used inside the Python environment.

* Here is an example of a Python script for generating the partial images without the ghost layer. You are free to do it differently.


| import matplotlib.pyplot as plt plt.imshow(source\_field\[1:-1, 1:-1\], origin='lower',            cmap='viridis', vmax=200) plt.colorbar() plt.axis('off') plt.savefig("output\_r"+str(py\_pcoord\[0\])+"x"                       \+str(py\_pcoord\[1\])                       \+"\_iter"+ str(iter\_id)) plt.close() |
| :---- |


* Below is an example of the partial images at iteration 0\.  
  ![][image1]![][image2]  
  ![][image3]![][image4]  
  * Note: It is also possible to generate global images via the pycall plugin. Please check in the solution folder.  
    

5. ### \[HDF5\_A\] Use HDF5 to save the simulation data to disk sequentially.

     
* Activate the decl\_hdf5 plugin with:


| plugins:   decl\_hdf5:     \- file: output\_rank${rank:01}\_iter${iteration:02}.h5       on\_event: loop       write:         temp: |
| :---- |


* Several attributes are necessary for the HDF5 plugin:  
  * filename: can be a mix of string and (meta)data $-expression.  
  * Similar to the Pycall plugin, we chose to trigger the HDF5 plugin with the on\_event method.  
  * Use the write keyword to specify the content to write in a list  
    To use the rank to name the file, you need to share it with PDI in advance. Declare the rank as metadata in config.yml so you can reference its value.

* Try to generate some output files and check the data size with

| h5dump \-A output.h5 |
| :---- |


  And you should have something similar to 

| GROUP "/" {    DATASET "temp" {       DATATYPE  H5T\_IEEE\_F64LE       DATASPACE  SIMPLE { ( 32, 22 ) / ( 32, 22 ) }    } } |
| :---- |


* The size (32,22) corresponds to the local size with 2 ghost layers. Now, we will remove the ghost layers in our output data using memory\_selection, which allows us to make a selection on the data passed to PDI from the simulation.


| write:   temp:     memory\_selection:       size: \[ '$local\_size\[0\]-2', '$local\_size\[1\]-2' \]        start: \[1, 1\] |
| :---- |


* Add the selection to the config.yml and run the test. You should encounter an error at runtime:


| \[PDI\] \*\*\* error: Error while triggering event \`loop': Config\_error: Incompatible selections while writing \`temp': \[ (1-30/0-31) (1-20/0-21) \] \-\> \[ (0-31/0-31) (0-21/0-21) \] |
| :---- |


  This error indicates that we have a size issue with our data. Each time the HDF5 plugin writes data to a file, if the HDF5 dataset is not defined explicitly, it uses the default dataset, which has the same size as the declared data. You can use the datasets attribute in order to specify the dataset in which the data will be written:


| \- file: output\_rank${rank:01}\_iter${iteration:02}.h5   datasets:     temp: { type: array, subtype: double,              size: \['$local\_size\[0\]-2', '$local\_size\[1\]-2'\]} |
| :---- |


* Note: you are not obliged to name the dataset the same name as the data. However, if you give a different name to the dataset (e.g., temp\_ds), then you need to add in config.yml:


| write:   temp:     dataset: temp\_ds |
| :---- |

* Now re-run the test, and the error should have disappeared.


6. ### \[HDF5\_B\] Use HDF5 to save the simulation data to disk in parallel.

   * In this exercise, we aim to save global data to a file for each iteration.  
   * To enable the parallel write with HDF5, we need to give it the context of the MPI communicator (MPI\_COMM\_WORLD) by activating the MPI plugin:  
     

| plugins:   mpi:   decl\_hdf5:     \- file: output\_iter${iteration:02}.h5       communicator: $MPI\_COMM\_WORLD |
| :---- |

     

* Similar to the previous exercise, we need to specify the datasets used in the HDF5 output file. **Attention**, it is the global size of the domain\! Hint: Use the psize with local\_size variables to define the correct global size.  
* Also, we need to use the dataset\_selection attribute to specify the starting position for each process’s data in the global dataset. Hint: Use the pcoord variable to determine the correct position.


7. ### \[HDF5\_C\] Use HDF5 to save the simulation data to disk in parallel.

   * This exercise allows you to put all the data into a single file. As HDF5 does not allow an unlimited dimension, unlike netCDF, you need to define the maximum number of iterations (max\_iter) and let the HDF5 plugin acknowledge this information to reserve the correct memory space for the dataset.  
   * Modify the datasets to extend their dimension to 3 (one for the time dimension, and 2 for the space dimension)  
   * The size of the temporal dimension is $max\_iter+1.  
   * Similarly, modify the dataset\_selection section to choose the correct size and start position to receive data from each MPI process.  
     

8. ### \[USER\_CODE\] Use the user\_code plugin to compute some numerical metrics

   * The user\_code plugin allows us to call a C function.  
   * This C function takes no arguments, but it can access the content of variables available in the PDI data store.  
   * In this exercise, we want to compute the sum of the temperature across the whole domain, and the result at each iteration will be written to a file.  
   * To write to a file, we must open and close it properly. We choose to use the on\_event trigger. We will trigger the initialization event before the temporal loop and a finalization event after it. Upon triggering of these events, a corresponding C function will be called to open and close the file.  
     

| plugins:    user\_code:      on\_event:        initialization:          open\_file: {}        finalization:          close\_file: {} |
| :---- |

     

* In main.c you need to implement routines for file opening and closing.


| void open\_file(void) {  // … only rank 0 will perform } void close\_file(void) {  // … only rank 0 will perform } |
| :---- |


* Similarly, when the loop event is triggered, we will call the function compute\_integral, which computes the integral. 


| void compute\_integral(void) {   // get the MPI rank   // use PDI\_access to get:   	// current iteration number    	// local grid size and the process grid size   	// current temperature field        // e.g.       // int \*iter;       // PDI\_access("iteration", (void\*\*)\&iter, PDI\_IN);       // PDI\_release("iteraion");       // use \*iter as the value of the iteration number   // compute the local 2D sum of the field     // get the global sum using MPI\_Allreduce   // use PDI\_release to release the buffer   // rank 0 writes the result in the file } |
| :---- |


* You may also need to modify the CMakeLists.txt file.


| add\_executable(main main.c) target\_link\_libraries(main m MPI::MPI\_C paraconf::paraconf PDI::pdi) set\_target\_properties(main PROPERTIES ENABLE\_EXPORTS TRUE) |
| :---- |


* You can compare the results with ”integral\_reference.dat”.

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAANUAAADGCAYAAABFAsW2AAAOfElEQVR4Xu2dbXCV5Z3G6e7iuo7sbGdXIUgSEom8yJsBBBEkhAMJToXBF0q1JlWhBAVUQORFgoHkSCQ5de1Suto367bQVti2U7quwgK7pdZaQIso2gZaaWVkptNR+8FxGP97zpkJk1x/4n+4+/R5zn33+s38Js958ciH6zcHPtx5egkhJFJ64ROEkD8PRkVIxDAqQiKGURESMYyKkIhhVIREDKMiJGIYFSERw6gIiRhGRUjEMCpCIoZRERIxjIqQiGFUhEQMoyIkYhgVIRHDqAiJGEZFSMQwKkIihlEREjGMipCIYVTEe1599VUpKSnJX+/YsUOKiory188//7yMGjWq61tjgVGRIOjVq5d0dHTkr2fNmiV79uzJX48cObLr22KBUTmQ+sTNBeXAx9q81OLEwVL5w5tlypMnT8q777579n2LFy/O/2RUHoOjTlocqy9anH6jVD54u0zZNagc+/btk1OnTuWvd+7cefavf7t37+Zf/3wBR520OFZftHj7jQHyp7dLlBhVocGoHMBRJy2O1Rctfnusv/zx9wOUjCpAcNRJi2P1RYuOY/3k9O/7KxlVgOCokxbH6osWb77eV079rkjJqAIER520OFZftDj6+qXy1u/6KRlVgOCokxbH6osWL792qXSc7KdkVAGCo05aHKsvWhx6ra+8ebJIyagCBEedtDhWX7R48Wg/OfpWfyWjChAcddziOH3V4qdHi+SXb12mZFQBgiOPWxynr1r8z6vF8vPflioZVYDgyOMWx+mrFnuOlMjPfjNQyagCBEcetzhOX7V47kipHPhNmZJRBQiOPG5xnL5qseuX5bLvRIWSUQUIjjxucZy+avGfr1TIc8eHKBlVgODI4xbH6asW33tliOw6fqWSUQUIjjxucZy+arH95WHyw44RSowqd4Q+R+5MVc7cYcUpU6acPWMVN4zKARx53OI4fdXi6cMjZMevRyvx5G9XWltb8z+feOIJ2bZtG7waD4zKARx53OI4fdXia4euku2/Gqv8uKhyv6uiK9u3b+/2OA4YlQM48rjFcfqqxZOHxsi3fnW1EoM6fPhw3hxbt27N/2xqapJdu3bJmTNnur41FhiVAzjyuMVx+qrF1kPj5BtvXqPEqAoNRuUAjjxucZy+avH4wQny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>

[image4]: <data:image/png;base64,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>