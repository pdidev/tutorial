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


def save_file(data, globalImageActor, block_info=None):
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
    
    globalImageActor.sub_image_saved(ts, x, y, filename)

    return data



class GenerateGlobalImage:

    def __init__(self):
        self.max_sub_domain = max_coord_x_y[0] * max_coord_x_y[1]
        self.current_sub_images = dict()  # {ts: [((x,y), f1), ((x,y), f1), ((x,y), f1), ((x,y), f1)]}

    def sub_image_saved(self, ts, x, y, filename):
        # print("> sub_image_saved: ts=" + str(ts) + ", x=" + str(x) + ", y=" + str(y) + ", filename=" + filename, flush=True)
        res = self.current_sub_images.get(ts, [])
        res.append(((x, y), filename))
        self.current_sub_images[ts] = res

        if len(res) == self.max_sub_domain:
            # all sub-images for this ts are saved, generate global image
            os.sync()  # force writing to disk
            self.stitch_images(ts, res)
            self.current_sub_images.pop(ts)  # remove the entry

    @staticmethod
    def concat_tile(list_2d):
        return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in list_2d])

    def stitch_images(self, ts, sub_images):
        assert len(sub_images) == self.max_sub_domain
        # print("> stitch_images: ts=" + str(ts) + ", sub_images=" + str(sub_images), flush=True)
        images = np.empty(shape=max_coord_x_y).tolist()

        try:
            for ((x, y), image_path) in sub_images:
                # print(">> reading image: x=" + str(x) + ", y=" + str(y) + ", image_path=" + image_path, flush=True)
                images[x][y] = cv2.imread(image_path)

            images = images[::-1]  # flip the image on x
            combined_image = self.concat_tile(images)
            cv2.imwrite("results/img/global/heat-" + str(ts).zfill(3) + ".png", combined_image)
        except Exception as e:
            print("Error combining images: " + str(e), flush=True)


future = client.submit(GenerateGlobalImage, actor=True)
globalImageActor = future.result()  # Get back a pointer to the actor

img_data = gt[0:max_ts:100, :, :]
print("> data=" + str(img_data), flush=True)
# img_data = img_data.rechunk({0: -1, 1: -1})
img_data = img_data.transpose()
# print("> data=" + str(img_data), flush=True)

f = img_data.map_blocks(save_file, globalImageActor, dtype=img_data.dtype)
arrays.validate_contract()
dask.compute(f)

print("Done", flush=True)
deisa.wait_for_last_bridge_and_shutdown()

