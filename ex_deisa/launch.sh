#!/bin/bash

#SBATCH --job-name=deisa_tutorial
#SBATCH --output=%x_%j.log
#SBATCH --time=00:20:00
#SBATCH --partition=cpu_short
#SBATCH --ntasks=7
#SBATCH --nodes=1

SIM_PROCESS=4
DASK_WORKERS=1
DASK_SCHEDULER_FILE=scheduler.json
PREFIX=deisa_tutorial

echo "Starting Dask scheduler"
mpirun -np 1 dask scheduler --scheduler-file=${DASK_SCHEDULER_FILE} &

while ! [ -f ${DASK_SCHEDULER_FILE} ]; do
    sleep 3
    echo -n .
done

# dask workers
mpirun -np ${DASK_WORKERS} dask worker --local-directory /tmp --scheduler-file=${DASK_SCHEDULER_FILE} &

echo "Starting in situ client"
mpirun -np 1 python client.py &
client_pid=$!

echo -n "Starting simulation in 3"
sleep 1; echo -n ", 2"
sleep 1; echo -n ", 1"
sleep 1; echo "   GO !"

mpirun -np ${SIM_PROCESS} build/deisa
#sleep 10

# When simulation is finished, kill mpi processes
echo "Simulation is finished."
wait $client_pid

echo "All done !"
