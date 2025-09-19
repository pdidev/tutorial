import matplotlib.pyplot as plt
import numpy as np

def plot_local_image(source_field, py_coord,  iter_id):
    plt.imshow(source_field[1:-1, 1:-1], cmap='viridis', vmax=200)
    plt.colorbar()
    plt.axis('off')
    plt.savefig("output_python_file_r"+str(py_coord[0])+"x"+str(py_coord[1])+"_iter"+str(iter_id))
    plt.close()


def plot_global_image(source_field, py_pcoord, iter_id):
    # Function to save the temperature solution in the global domain
    # Remark: This implementation is only a proof of concept. 
    #         Therefore, it is not perhaps optimal.
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    # get the size of cart_comm in each direction
    py_psize = np.zeros(2, dtype=np.int32)
    comm.Allreduce(py_pcoord,py_psize,op=MPI.MAX)
    py_psize[0] = py_psize [0] + 1
    py_psize[1] = py_psize [1] + 1
    assert( size == (py_psize[0]*py_psize[1]) )

    # get the size of the local domain (including the ghost)
    py_local_size = np.shape(source_field)

    global_size = np.zeros(2, dtype=np.int32)
    global_size[0] = py_psize[0]*(py_local_size[0]-2)
    global_size[1] = py_psize[1]*(py_local_size[1]-2)

    ## Object for sending buffer 
    ## view for the simulation data to remove ghost cells
    shape_array_view_sim_data = [py_local_size[0],py_local_size[1]]
    shape_subarray_view_sim_data = [py_local_size[0]-2,py_local_size[1]-2]
    start_coord_view_sim_data = [1,1]

    type_subarray_view_sim_data = MPI.DOUBLE.Create_subarray(shape_array_view_sim_data,\
                            shape_subarray_view_sim_data,start_coord_view_sim_data,MPI.ORDER_C)
    type_subarray_view_sim_data.Commit()

    ## Object for receiving buffer
    ## vector for the gather receiver
    lenghts = np.ones( size, dtype=np.int32)
    displacements = np.zeros( size, dtype=np.int32)
    displacements_all = np.zeros( size, dtype=np.int32)

    ## view for the gather receiver
    shape_array_view = [global_size[0], global_size[1]]
    shape_subarray_view = [py_local_size[0]-2,py_local_size[1]-2]
    start_coord_view = [0,0]

    type_subarray_view = MPI.DOUBLE.Create_subarray(shape_array_view,\
                            shape_subarray_view,start_coord_view,MPI.ORDER_C)
    type_subarray_view.Commit()

    # extent = MPI.DOUBLE.Get_size() * (py_local_size[0]-2)   ## Row major  (Fortran)
    extent = MPI.DOUBLE.Get_size() * (py_local_size[1]-2)   ## Colum major
    type_slice = type_subarray_view.Create_resized(0,extent)
    type_slice.Commit()

    # displacements[rank] = py_psize[0]*py_pcoord[1]*(py_local_size[1]-2) + py_pcoord[0]  ## Row major (Fortran)
    displacements[rank] = py_psize[1]*py_pcoord[0]*(py_local_size[0]-2) + py_pcoord[1]  ## Colum major
    comm.Allreduce(displacements,displacements_all,op=MPI.SUM)

    if rank == 0:
        Global_solution = np.zeros((global_size[0],global_size[1]), dtype=np.float64)
    else:
        Global_solution = None

    # MPI communication with "Gatherv"
    comm.Gatherv([source_field, 1, type_subarray_view_sim_data], [Global_solution, lenghts, displacements_all, type_slice], root=0)

    ## For explication of lenghts, displacements_all, type_slice,
    ## see https://stackoverflow.com/questions/9269399/sending-blocks-of-2d-array-in-c-using-mpi/9271753#9271753

    if rank == 0:
        plt.imshow(Global_solution, origin='lower', cmap='viridis', vmax=200)
        plt.savefig("output_global_domain_iter"+str(iter_id))