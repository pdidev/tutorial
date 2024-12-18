import sys
import dask
import numpy as np
import dask.array as da
from dask.distributed import Client, Event, get_client, comm, Queue, Future, Variable
from dask.delayed import Delayed
import time
import asyncio
import json
import itertools


class metadata:
    index = list()
    data = ""
    shap = None
    typ = ""
    def __init__(self, name):
        self.name = name

def connect(sched_file):
    sched = ''.join(chr(i) for i in sched_file)
    with open(sched[:-1]) as f:
        s = json.load(f)
    adr = s["address"]
    client  = get_client(adr)
    return client


def init(sched_file, rank, size, arrays, deisa_arrays_dtype):
    client = connect(sched_file)
    return Bridge(client, size, rank, arrays, deisa_arrays_dtype)

class Bridge:
    workers = []
    def __init__(self, Client, Ssize, rank, arrays, deisa_arrays_dtype):
        self.client  = Client
        self.rank = rank
        listw = Variable("workers").get()
        if Ssize > len(listw): # more processes than workers
            self.workers = [listw[rank%len(listw)]]
        else:
            k = len(listw)//Ssize # more workers than processes
            self.workers = listw[rank*k:rank*k+ k]
        self.arrays = arrays
        for ele in self.arrays:
            self.arrays[ele]["dtype"] = str(deisa_arrays_dtype[ele])
            self.arrays[ele]["timedim"] = self.arrays[ele]["timedim"][0]
            self.position = [self.arrays[ele]["starts"][i]//self.arrays[ele]["subsizes"][i] for i in range(len(np.array(self.arrays[ele]["sizes"])))]
        if rank==0:
            Queue("Arrays").put(self.arrays) # If and only if I have a perfect domain decomposition 
        
            
    def create_key(self, timestep, name):
        self.position[self.arrays[name]["timedim"]]= timestep
        position = tuple(self.position)
        return ("deisa-"+name, position)

    def publish_data(self, data, data_name, timestep):
        event = Event("Done")
        if (timestep==0):
            event.wait()
        key = self.create_key(timestep, data_name)
        shap = list(data.shape)
        new_shape = tuple(shap[:self.arrays[data_name]["timedim"]]+[1]+shap[self.arrays[data_name]["timedim"]:])
        data.shape = new_shape #will not copy, if not possible raise an error so handle it :p 
        #data = data.reshape(new_shape)
        f = self.client.scatter(data, direct = True, workers=self.workers, keys=[key], deisa=True)
        while (f.status != 'finished'):
            f = self.client.scatter(data, direct = True, workers=self.workers, keys=[key], deisa=True)
        data=None
class Adaptor :
    adr = ""
    client = None
    workers = []
    queues = []
    def __init__(self, Sworker, scheduler_info):
        with open(scheduler_info) as f:
            s = json.load(f)
        self.adr = s["address"]
        self.client  = Client(self.adr, serializers=['dask', 'pickle']) # msgpack pour grand message ne serialize pas
        dask.config.set({"distributed.deploy.lost-worker-timeout": 60, "distributed.workers.memory.spill":0.97, "distributed.workers.memory.target":0.95, "distributed.workers.memory.terminate":0.99 })
        self.workers = [comm.get_address_host_port(i,strict=False) for i in self.client.scheduler_info()["workers"].keys()]
        while (len(self.workers)!= Sworker):
            self.workers = [comm.get_address_host_port(i,strict=False) for i in self.client.scheduler_info()["workers"].keys()]
        Variable("workers").set(self.workers)
        

    def create_array(self, name, shape, chunksize, dtype, timedim):
        chunks_in_each_dim = [shape[i]//chunksize[i] for i in range(len(shape))]
        l = list(itertools.product(*[range(i) for i in chunks_in_each_dim]))
        items = []
        for m in l:
            f=Future(key=("deisa-"+name,m), inform=True, deisa=True)
            d = da.from_delayed(dask.delayed(f), shape=chunksize, dtype=dtype)
            items.append([list(m),d])
        ll = self.array_sort(items)
        arrays = da.block(ll)
        return arrays
    
    def create_array_list(self, name, shape, chunksize, dtype, timedim): #list arrays, one for each time step.
        chunks_in_each_dim = [shape[i]//chunksize[i] for i in range(len(shape))]
        l = list(itertools.product(*[range(i) for i in chunks_in_each_dim]))
        items = []
        for m in l:
            f=Future(key=("deisa-"+name,m), inform=True, deisa=True)
            d = da.from_delayed(dask.delayed(f), shape=chunksize, dtype=dtype)
            items.append([list(m),d])
        ll = self.array_sort(items)
        for i in ll:
            arrays.append(da.block(i))
        return arrays
    
    def array_sort(self, ListDs):
        if len(ListDs[0][0]) == 0:
            return ListDs[0][1]
        else:
            dico = dict()
            for e in ListDs:
                dico.setdefault(e[0][0],[]).append([e[0][1:], e[1]])
            return [self.array_sort(dico[k]) for k in sorted(dico.keys())]

    def get_data(self, as_list=False):
        arrays = dict()
        self.arrays_desc = Queue("Arrays").get()
        for name in self.arrays_desc:
            if not as_list:
                arrays[name] = self.create_array(name,self.arrays_desc[name]["sizes"], self.arrays_desc[name]["subsizes"], self.arrays_desc[name]["dtype"], self.arrays_desc[name]["timedim"])
            else: #TODO test this 
                arrays[name] = self.create_array_list(name,self.arrays_desc[name]["sizes"], self.arrays_desc[name]["subsizes"], self.arrays_desc[name]["dtype"], self.arrays_desc[name]["timedim"])
        #Barrier after the creation of all the dask arrays 
        e = Event("Done")
        e.set()
        return arrays

def Initialization(Sworker, scheduler_info):
    return Adaptor(Sworker, scheduler_info)

