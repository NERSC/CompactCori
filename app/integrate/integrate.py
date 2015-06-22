from mpi4py import MPI as mpi
from scipy import integrate as sci_integrate
import numpy as np

comm = mpi.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

def parallel_integrate(start, end, function = np.sin, num_samples = 100000):
    width = (end - start)/(num_samples*size)

    # Where this thread starts integrating
    local_start = start + width*num_samples*rank
    local_end   = local_start + width*num_samples

    area = np.zeros(1)

    if rank:
        totalArea = None
    else:
        totalArea = np.zeros(1)

    for i in range(num_samples):
        height = function(local_start + i*width)
        area += width * height

    comm.Reduce(area, totalArea, root=0)

    if not rank:
        print(totalArea)

# execute main
if __name__ == "__main__":
    parallel_integrate(0, np.pi)
    parallel_integrate(0, 2*np.pi)

