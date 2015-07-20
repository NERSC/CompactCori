#!/usr/bin/python
"""A parallelized MD simulation in Python written for version 1 of the Compact Cori
project at NERSC.

This runs in O(n^2) time since all particles are compared to one another when
locating in-range neighbors.

Threads in mpi4py are 0-indexed
"""
import Partition
import Particle

import argparse
import random
import math
import numpy as np
import threading
import json
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler
from mpi4py import MPI as mpi

comm = mpi.COMM_WORLD
rank = comm.Get_rank()
num_threads = comm.Get_size()

max_radius = 1000

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--numparticles", type=int,
        help = "number of particles in simulation")
parser.add_argument("-r", "--radius", type=int,
        help = "radius of particle interaction")
parser.add_argument("--height", type=int,
        help = "height of simulation ")
parser.add_argument("--width", type=int,
        help = "width of simulation ")
parser.add_argument("--depth", type=int,
        help = "depth of simulation ")
parser.add_argument("-d", "--dt", type=float,
        help = "time constant")
args = parser.parse_args()

num_particles = args.numparticles if args.numparticles else 20
radius = args.radius if args.radius else 100
simulation_height = args.height if args.height else 1000
simulation_width = args.width if args.width else 1000
simulation_depth = args.depth if args.depth else 1000
dt = args.dt if args.dt else 0.0005

particles = []

# TODO: Remove typechecking for production
def validate_int(*args):
    for arg in args:
        if type(arg) is not int:
            error(ArgumentError, "incorrect type argument: " + type(arg) +
                "was passed instead of a int")

def validate_list(*args):
    for arg in args:
        if type(arg) is not list:
            error(ArgumentError, "incorrect type argument: " + type(arg) +
                "was passed instead of a int")

def validate_particle_set(*args):
    for arg in args:
        if type(arg) is not set:
            error(ArgumentError, "incorrect type argument: " + type(arg) +
                "was passed instead of a set")
        for obj in arg:
            if type(obj) is not Particle:
                error(ArgumentError, "Non-particle type in set; received a " +
                        type(obj) + " instead of a Particle")

def debug(string):
    """Print a message in yellow to STDOUT"""
    CSI="\x1B["
    print(CSI + "31;93m" + "[DEBUG]    " + string + CSI + "31;0m")

def error(err, string):
    """Print a message in red to STDOUT and raise an exception"""
    CSI="\x1B["
    print(CSI + "31;31m" + "[ERROR]    " + string + CSI + "31;0m")
    raise err(CSI + "31;31m" + string + CSI + "31;0m")


def disable_partition(partition):
    if type(partition) is not Partition:
        raise TypeError("A " + type(partition) + " was passed to disable_partition")
    partition.active = False
    # TODO Update neighbor partitions

def enable_partition(partition):
    if type(partition) is not Partition:
        raise TypeError("A " + type(partition) + " was passed to disable_partition")
    partition.active = True
    # TODO Update neighbor partitions

# Create Partitions and set neighbors
partitions = []
for i in range(num_threads):
    partitions.append(Partition(i))

# Create Particles for Parallel Processes
for _ in range(num_particles):
    curr_particle = Particle()

    particles.append(Particle())

# One timestep
def timestep():
    if rank is 0:
        particles = []
        buff = []
        for i in range(1,num_threads):
            comm.Recv(buff, source = mpi.ANY_SOURCE)
            particles += buff
    else:
        partition = partitions[rank]
        partition.update_neighbor_thread_set()

        right, left = partition.handoff()

        # Update neighbors with my particles
        if partitions[rank - 1].active:
            comm.Send(left , dest = rank - 1)
        if partitions[rank + 1].active:
            comm.Send(right, dest = rank + 1)
        # Receive particles from neighbors
        neighbor_particles = []
        for _ in parition.neighbor_threads:
            comm.Recv(neighbor_particles, source = mpi.ANY_SOURCE)

        # Do computation
        for particle in partition.particles:
            particle.populate_neighbors(partition.particles + neighbor_particles)
        for particle in partition.particles:
            particle.update_velocity()
        for particle in partition.particles:
            particle.update_position(dt)

        right, left = [], []
        for particle in particles:
            # Check to see if the particle is in this partition still, if not,
            # populate the lists
            pass

        # Send neighbors their new particles
        if partitions[rank - 1].active:
            comm.Send(left , dest = rank - 1)
        if partitions[rank + 1].active:
            comm.Send(right, dest = rank + 1)

        # Receive particles from neighbors
        new_particles = []
        for _ in parition.neighbor_threads:
            comm.Recv(new_particles, source = mpi.ANY_SOURCE)
        partition.add_particles(new_particles)

        # Update root
        comm.Send(partition.particles)

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to the API endpoint"""
        global endpoint
        parsed_path = urlparse(self.path)
        if "/api/v1/get_particles" in parsed_path:
            message = "\r\n".join(endpoint)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        else:
            debug("GET request sent to " + parsed_path)

    def do_POST(self):
        """Handle POST requests to the API endpoint"""
        global endpoint
        parsed_path = urlparse(self.path)
        if "/api/v1/post_parameters" in parsed_path:
            length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(length).decode("utf-8")
            # Parse data from POST

#            # Print for debugging
            pass
#            self.wfile.write(str(post_data).encode("utf-8"))
#            self.wfile.write("\n".encode("utf-8"))
        else:
            debug("POST request sent to " + parsed_path)

endpoint = "{\n}"
def main():
    global endpoint
    from http.server import HTTPServer
    server = HTTPServer(("127.0.0.1", 8080), Server)
    print("Starting server, ^c to exit")
    threading.Thread(target=server.serve_forever).start()
    while True:
        timestep()
        # Use a copy of endpoint to prevent queries to endpoint from
        # receiving an in-progress timestep
        temp_endpoint = "{\n"
        for particle in particles:
            temp_endpoint += json.dumps(particle, default=lambda obj: obj.__dict__, sort_keys = True, indent=2)
        temp_endpoint += "\n}"
        endpoint = temp_endpoint

if __name__ == "__main__":
    main()
