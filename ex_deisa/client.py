import yaml
from dask_interface import Initialization
import dask
import dask.array as da
from dask.distributed import performance_report

# Get configuration
with open(r'config.yml') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
    Sworkers = data["workers"]

# Scheduler file name 
scheduler_info = 'scheduler.json'

# Initialize the Deisa Adaptor 
Adaptor = Initialization(Sworkers, scheduler_info)

# Check if client version is compatible with scheduler version
Adaptor.client.get_versions(check=True)

# Get data descriptor as a dict of Dask arrays
arrays = Adaptor.get_data()

# py-bokeh is needed if you wanna see the perf report 
with performance_report(filename="dask-report.html"):
    # Get the Dask array global_t
    gt = arrays["global_t"]    
    #gt = gt.rechunk({1: 'auto', 2: 'auto'})
    print(gt.chunks)
    # Construct a lazy task graph 
    cpt = (gt.sum() - gt.mean())*5.99 /  gt.mean() 
    # Submit the task graph to the scheduler
    s = Adaptor.client.compute(cpt, release=True)
    # Print the result, note that "s" is a future object, to get the result of the computation, we call `s.result()` to retreive it.  
    print(s.result())
