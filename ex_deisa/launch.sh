#!/bin/bash

#SBATCH -J dask-cluster
#SBATCH -A dask_coupling
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --partition=cpu_med
#SBATCH --exclusive


NPROC=4                          # Total number of processes
NPROCPNODE=4                     # Number of processes per node
NWORKERPNODE=4                  # Number of Dask workers per node

SCHEFILE=scheduler.json

# Launch Dask Scheduler in a 1 Node and save the connection information in $SCHEFILE
echo launching Scheduler 
srun --cpu-bind=verbose --ntasks=1 --nodes=1 -l \
    --output=scheduler.log \
    dask-scheduler \
    --interface ib0 \
    --scheduler-file=$SCHEFILE   &

# Wait for the SCHEFILE to be created 
while ! [ -f $SCHEFILE ]; do
    sleep 1
    echo -n .
done

# Connect the client to the Dask scheduler
echo Connect Master Client  
`which python` client.py &
client_pid=$!

# Launch Dask workers in the rest of the allocated nodes 
echo Scheduler booted, Client connected, launching workers 
srun  --cpu-bind=verbose  -l \
     --output=worker-%t.log \
     dask-worker \
     --interface ib0 \
     --local-directory /tmp \
     --nprocs $NWORKERPNODE \
     --scheduler-file=${SCHEFILE} &
     
# Launch the simulation code
echo Running Simulation 
srun  --ntasks=$NPROC --ntasks-per-node=$NPROCPNODE  -l ./simulation  &

# Wait for the client process to be finished 
wait $client_pid


