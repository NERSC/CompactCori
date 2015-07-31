#!/usr/bin/python
"""A parallelized MD simulation in Python written for version 1 of the Compact Cori
project at NERSC.

Only the master node has an accurate params file.  Slaves know the number of
active workers, but other parameters are not guaranteed to be accurate.

Threads are 0-indexed

The master node does not do any computational work.

Threads 1-n correspond to the n partitions that do computational work.

Speedup could possibly occur by using numpy instead of arrays/lists
"""
from Partition import Partition
from Particle import Particle
import util
import params

import argparse
import random
import math
import threading
import json
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler
from mpi4py import MPI as mpi

params.mpi = mpi
params.comm = mpi.COMM_WORLD
params.rank = params.comm.Get_rank()
params.num_threads = params.comm.Get_size()
params.mpi_status = mpi.Status()

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--numparticles", type=int,
        help = "number of particles in simulation")
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
params.simulation_height = args.height if args.height else 1000
params.simulation_width = args.width if args.width else 1000
params.simulation_depth = args.depth if args.depth else 1000
params.dt = args.dt if args.dt else 0.0005
params.num_active_workers = 0
params.new_num_active_workers = 0
params.max_radius = min(params.simulation_width, params.simulation_height, params.simulation_depth)//32
params.partitions = {}

# Create partitions 1 through params.num_threads - 1
for i in range(1, params.num_threads):
    params.partitions[i] = Partition(i)

# Create Particles for Partitions
for i in range(params.num_particles):
    radius = random.randint(0, params.max_radius)
    position = [random.randint(radius, params.simulation_width - 1),
                random.randint(radius, params.simulation_height - 1),
                random.randint(radius, params.simulation_depth - 1)]
    velocity = [random.randint(0,5),
                random.randint(0,5),
                random.randint(0,5)]
    mass = random.randint(1,10)
    if radius > params.max_radius:
        util.debug("Radius is greater than 1/32 of the simulation")
    thread_num = util.determine_particle_thread_num(position[0])
    new_particle = Particle(i, thread_num, position, velocity, mass, radius)
    params.partitions[thread_num].add_particle(new_particle)

def update_params():
    params.comm.bcast(params.num_active_workers)

# One timestep
def timestep():
    """Only do something as a slave if an active worker"""
    if params.rank is 0:
        for i in range(1, params.num_threads):
            new_particles = params.comm.recv(source = mpi.ANY_SOURCE, status = params.mpi_status, tag = 00)
            params.partitions[params.mpi_status.Get_source()].particles = new_particles
    elif params.rank <= params.num_active_workers:
        partition = params.partitions[params.rank]
        partition.send_and_receive_neighboring_particles()
        partition.interact_particles()
        partition.exchange_particles()
        partition.update_master()

def change_num_active_workers(new_num_active_workers):
    if params.rank is 0:
        if new_num_active_workers < 1 or new_num_active_workers > params.num_threads - 1:
            util.debug("Invalid number of active workers requested: " + new_num_active_workers)

        new_distribution = {}
        for i in range(1, new_num_active_workers + 1):
            new_distribution[i] = set()

        for partition_id, partition in params.partitions:
            for particle in partition.particles:
                new_thread = util.determine_particle_thread_num(particle.position[0], new_num_active_workers)
                particle.thread_num = new_thread
                new_distribution[new_thread].add(particle)

        for i in range(1, new_num_active_workers + 1):
            params.comm.send(new_distribution[i], dest = i, tag = 11)
    else:
        params.partitions[params.rank].receive_new_particles()

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to the API endpoint"""
        global endpoint
        parsed_path = urlparse(self.path)
        if "/api/v1/get_particles" in parsed_path:
#            message = "\r\n".join(endpoint)
            message = "\r\n".join("TEST MESSAGE")
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        else:
            util.info("GET request sent to " + parsed_path)

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
            util.info("POST request sent to " + parsed_path)

endpoint = "{\n}"
def main():
    global endpoint
    from http.server import HTTPServer

    port_number = 8080
    server = HTTPServer(("127.0.0.1", port_number), Server)
#    print("Starting server on port " +  str(port_number) + ", ^c to exit")
#    threading.Thread(target=server.serve_forever).start()

    count = 0
    while True:
        util.info("Timestep " + str(count))
        count += 1
        timestep()
        update_params()
        if params.new_num_active_workers is not params.num_active_workers:
            change_num_active_workers(params.new_num_active_workers)
#        else:
#            continue_with_same_number_of_workers()

        # Use a copy of endpoint to prevent queries to endpoint from
        # receiving an in-progress timestep
        temp_endpoint = "{\n"
        temp_endpoint += "\"params\":[\n"
        temp_endpoint += "  \"num_particles\": " + str(params.num_particles) + ",\n"
        temp_endpoint += "  \"num_active_workers\": " + str(params.num_active_workers) + ",\n"
        temp_endpoint += "  \"simulation_height\": " + str(params.simulation_height) + ",\n"
        temp_endpoint += "  \"simulation_width\": " + str(params.simulation_width) + ",\n"
        temp_endpoint += "  \"simulation_depth\": " + str(params.simulation_depth) + ",\n"
        temp_endpoint += "  \"simulation_depth\": " + str(params.simulation_depth) + ",\n"
        temp_endpoint += "]\n"
        temp_endpoint += "\"particles\":[\n"
        for key, partition in params.partitions.items():
            for particle in partition.particles:
                temp_endpoint += "    " + json.dumps(particle, default=lambda obj: obj.__dict__, sort_keys = True, indent=2)
        temp_endpoint += "\n]\n}"
        endpoint = temp_endpoint

if __name__ == "__main__":
    main()
