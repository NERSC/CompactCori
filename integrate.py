import numpy as np
import scipy as sp
from mpi4py import MPI as mpi

comm = mpi.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def integrate(start, end, function = numpy.sin, num_samples = 100):
    width = (end - start)/(num_samples*size)

    # Where this thread starts integrating
    local_start = start + width * rank * num_samples
    local_end = local_start + width*num_samples

    area = np.zeros(1)

    if rank:
        local_area = np.zeros(1)
    else:
        local_area = None

    for i in range(num_samples):
        height = function(start + i*width)
        area += width * height

    comm.Reduce(area, localarea)

    # Only the root node prints the area
    if not rank:
        print(area)

integrate(0,10*np.pi)
