#!/bin/bash
SIMU_NPROC=1                     # Number of simulation processes
DASK_NB_WORKERS=1                # Number of Dask workers
DASK_NB_THREAD_PER_WORKER=1      # Number of threads per Dask workers

SCHEFILE=scheduler.json

# Launch Dask Scheduler in a 1 Node and save the connection information in $SCHEFILE
echo launching Scheduler
dask scheduler \
    --interface lo \
    --scheduler-file=$SCHEFILE &
dask_sch_pid=$!

# Wait for the SCHEFILE to be created 
while ! [ -f $SCHEFILE ]; do
    sleep 1
    echo -n .
done

echo Scheduler booted, launching workers
dask worker \
    --interface lo \
    --nworkers ${DASK_NB_WORKERS} \
    --nthreads ${DASK_NB_THREAD_PER_WORKER} \
    --local-directory /tmp \
    --scheduler-file=${SCHEFILE} &
dask_worker_pid=$!

sleep 1

# Launch the analytics
#echo Running analytics
#python client.py &
#analytics_pid=$!

sleep 1

# Launch the simulation code
echo Running Simulation 
mpirun --allow-run-as-root -np ${SIMU_NPROC} ./main

sleep 1

kill -9 ${dask_worker_pid} ${dask_sch_pid}
