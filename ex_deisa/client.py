# =============================================================================
# Copyright (C) 2015-2025 Commissariat a l'energie atomique et aux energies alternatives (CEA)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

import dask.array as da
import numpy as np
import yaml
import os
from deisa.dask import Deisa, get_connection_info

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

deisa = Deisa(get_connection_info=lambda: get_connection_info(config['dask_addr']))
nb_iterations = 10


class GenerateGlobalImage:
    def __init__(self):
        # print("> GenerateGlobalImage.__init__", flush=True)
        self.max_sub_domain = 1
        self.max_coord_x_y = (1, 1)
        self.current_sub_images = dict()

    def sub_image_saved(self, ts, x, y, filename):
        try:
            # print(f"> sub_image_saved: ts={ts}, x={x}, y={y}, filename={filename}", flush=True)
            res = self.current_sub_images.get(ts, [])
            res.append(filename)
            self.current_sub_images[ts] = res

            if len(res) == self.max_sub_domain:
                GenerateGlobalImage.stitch_iteration_to_png(res, ts, f"results/img/global/heat-{ts}.png")
                self.current_sub_images.pop(ts)  # remove the entry
        except Exception as e:
            print("Error saving sub-image: " + str(e), flush=True)

    @staticmethod
    def stitch_iteration_to_png(
            image_paths,
            iteration,
            output_path,
            pattern=r".*-(\d+)-(\d+)-(\d+)\.png",
            background_color=(0, 0, 0)
    ):
        """
        Stitch images whose filenames encode (iteration, x, y) and write to disk.

        Example filename:
            heat-0-0-0.png   -> iter=0, x=0, y=0

        Parameters
        ----------
        image_paths : list[str | Path]
            Input image files.
        iteration : int
            Iteration to stitch.
        output_path : str | Path
            Output PNG file path.
        pattern : str
            Regex extracting (iter, x, y).
        background_color : tuple
            RGB background color.
        """
        import re
        from pathlib import Path
        from PIL import Image

        tiles = {}

        for path in map(Path, image_paths):
            print(f">>>> path={path}", flush=True)
            m = re.match(pattern, path.name)
            if not m:
                continue

            it, x, y = map(int, m.groups())
            if it == iteration:
                tiles[(x, y)] = Image.open(path).convert("RGB")

        if not tiles:
            raise ValueError(f"No images found for iteration {iteration}")

        xs = sorted({x for x, _ in tiles})
        ys = sorted({y for _, y in tiles})

        tile_w, tile_h = next(iter(tiles.values())).size

        stitched = Image.new(
            "RGB",
            (tile_w * len(xs), tile_h * len(ys)),
            background_color
        )

        # y=0 at bottom (simulation-style coordinates)
        for (x, y), img in tiles.items():
            px = xs.index(x) * tile_w
            py = (len(ys) - 1 - ys.index(y)) * tile_h
            stitched.paste(img, (px, py))

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        stitched.save(output_path, format="PNG")


def save_file(data, globalImageActor, timestep, block_info=None):
    # imports are done here to avoid issues with dask (multiprocessing)

    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt

    if block_info:
        """ Save file to heat-t-x-y.tif, where x and y are block locations """
        # print("> save_file: data=" + str(data), flush=True)
        # print("> save_file: block_info=" + str(block_info[0]), flush=True)
        x = block_info[0]["chunk-location"][0]
        y = block_info[0]["chunk-location"][1]

        filename = "results/img/partial/heat-" + str(timestep) + "-" + str(x) + "-" + str(y) + ".png"

        # TODO: find a way to make matplotlib faster !
        fig, axe = plt.subplots()
        axe.pcolormesh(data[1:-1, 1:-1], cmap='plasma', vmin=0, vmax=1)
        axe.axis("off")
        fig.savefig(filename, bbox_inches='tight', pad_inches=0)
        plt.close("all")

        globalImageActor.sub_image_saved(timestep, x, y, filename)


# create results folders
os.makedirs("results/img/partial", exist_ok=True)
os.makedirs("results/img/global", exist_ok=True)

max_sub_domain = (config['global_size']['height'] // config['parallelism']['height']) * (
        config['global_size']['width'] // config['parallelism']['width'])
max_coord_x_y = (config['parallelism']['height'], config['parallelism']['width'])

future = deisa.client.submit(GenerateGlobalImage, actor=True)  # Create a Counter on a worker
globalImageActor = future.result()  # Get back a pointer to that object

for i in range(nb_iterations):
    darr, it = deisa.get_array('my_array')
    print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
          f" Timestep {it} "
          f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    darr.map_blocks(save_file,
                    globalImageActor=globalImageActor,
                    timestep=int(it),
                    dtype=darr.dtype).compute()

deisa.close()
