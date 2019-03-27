#!/bin/bash
#@ class            = clallmds
#@ job_name         = PDI_ex2
#@ total_tasks      = 1
#@ node             = 1
#@ wall_clock_limit = 00:01:00
#@ output           = $(job_name).$(jobid).log
#@ error            = $(job_name).$(jobid).err
#@ job_type         = mpich
#@ environment      = COPY_ALL 
#@ queue
. /gpfslocal/pub/pdi/training-env.bash

mpirun -n $LOADL_TOTAL_TASKS ./ex2
