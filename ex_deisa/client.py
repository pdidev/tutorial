import os

import dask
import numpy as np
import yaml
from deisa import Deisa

# Scheduler file name and configuration file
scheduler_info_file = 'scheduler.json'
sim_info_file = 'deisa.yml'

with open(sim_info_file) as f:
    sim_info = yaml.load(f, Loader=yaml.FullLoader)

max_coord_x_y = (sim_info["parallelism"]["height"], sim_info["parallelism"]["width"])
local_mesh_size = (sim_info["global_size"]["height"] / max_coord_x_y[0], sim_info["global_size"]["width"] / max_coord_x_y[1])

# Initialize Deisa
deisa = Deisa(scheduler_info_file, nb_workers=1, use_ucx=False)
print(">>>> Deisa", flush=True)

# Get client
client = deisa.get_client()

# either: Get data descriptor as a list of Deisa arrays object
arrays = deisa.get_deisa_arrays()
print("in-situ: arrays.arrays=", arrays.arrays, flush=True)
print("in-situ: arrays.contract=", arrays.contract, flush=True)

# Select data
gt = arrays["global_t"][...]
max_ts = len(gt[:, 0, 0])
print("gt=" + str(gt), flush=True)
print("max_ts=" + str(max_ts), flush=True)

# Check contract
arrays.check_contract()
print("in-situ: arrays.arrays=", arrays.arrays, flush=True)
print("in-situ: arrays.contract=", arrays.contract, flush=True)

# create results folders
os.makedirs("results/img/partial", exist_ok=True)


def save_file(data, block_info=None):
    # imports are done here to avoid issues with dask (multiprocessing)
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import matplotlib.style as mplstyle
    mplstyle.use('fast')

    """ Save file to heat-t-x-y.tif, where x and y are block locations """
    # print("> save_file: data=" + str(data), flush=True)
    # print("> save_file: block_info=" + str(block_info), flush=True)
    x = block_info[0]["chunk-location"][0]
    y = block_info[0]["chunk-location"][1]
    ts = block_info[0]["chunk-location"][2]

    filename = "results/img/partial/heat-" + str(ts).zfill(3) + "-" + str(x) + "-" + str(y) + ".jpg"

    fig, axe = plt.subplots()
    axe.pcolormesh(data[1:-1, 1:-1, 0], cmap='plasma', vmin=0, vmax=1)
    axe.axis("off")

    fig.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=100)
    # plt.close(fig)
    plt.close("all")


    return data





img_data = gt[0:1001:100, :, :]
print("> data=" + str(img_data), flush=True)
# img_data = img_data.rechunk({0: -1, 1: -1})
img_data = img_data.transpose()
# print("> data=" + str(img_data), flush=True)

f = img_data.map_blocks(save_file, dtype=img_data.dtype)
arrays.validate_contract()
dask.compute(f)

print("Done", flush=True)
deisa.wait_for_last_bridge_and_shutdown()

