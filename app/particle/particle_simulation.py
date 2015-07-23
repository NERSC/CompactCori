#!/usr/bin/python
"""A parallelized MD simulation in Python written for version 1 of the Compact Cori
project at NERSC.

This runs in O(n^2) time since all particles are compared to one another when
locating in-range neighbors.

Threads in mpi4py are 0-indexed
"""
import Partition
import Particle
import util
import params

import argparse
import random
import math
import numpy as np
import threading
import json
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler
from mpi4py import MPI as mpi

params.comm = mpi.COMM_WORLD
params.rank = params.comm.Get_rank()
params.num_threads = params.comm.Get_size()

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

params.num_particles = args.numparticles if args.numparticles else 20
params.radius = args.radius if args.radius else 100
params.simulation_height = args.height if args.height else 1000
params.simulation_width = args.width if args.width else 1000
params.simulation_depth = args.depth if args.depth else 1000
params.dt = args.dt if args.dt else 0.0005
params.num_active_workers = 0
params.partitions = []

# OOB?
for i in range(1, params.num_threads + 1):
    params.partitions[i] = Partition(i)

# Create Particles for Partitions
for i in range(num_particles):
    position = [0, 0, 0]
    velocity = [0, 0, 0]
    mass = 0
    radius = 0
    if radius > params.max_radius:
        util.debug("Radius is greater than 1/32 of the simulation")
    thread_num = params.determine_particle_thread_num(position[0])
    new_particle = Particle(i, thread_num, position, velocity, mass, radius)
    partitions[thread_num].add_particle(new_particle)

# One timestep
def timestep():
    if rank is 0:
        particles = []
        buff = []
        for i in range(1, params.num_threads):
            params.comm.Recv(buff, source = mpi.ANY_SOURCE)
            particles += buff
    else:
        partition = partitions[rank]
        partition.send_and_receive_neighboring_particles()
        partition.interact_particles()
        partition.exchange_particles()
        partition.update_master()


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
            util.debug("GET request sent to " + parsed_path)

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
            util.debug("POST request sent to " + parsed_path)

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
