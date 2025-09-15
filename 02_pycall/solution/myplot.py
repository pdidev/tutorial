import matplotlib.pyplot as plt


def plot_global_image(source_field, coord, iter_id):
    plt.imshow(source_field[1:-1, 1:-1], cmap='viridis', vmax=200)
    plt.colorbar()
    plt.axis('off')
    plt.savefig("output_g_r"+str(coord[0])+"x"+str(coord[1])+"_iter"+str(iter_id))
    plt.close()
