#!/usr/bin/python
"""A parallelized MD simulation in Python written for version 1 of the Compact Cori project at NERSC.

Only the master node has an accurate params file.  Slaves know the number of
active workers, but other parameters are not guaranteed to be accurate.

Threads are 0-indexed

The master node does not do any computational work.

Threads 1-n correspond to the n partitions that do computational work.

Speedup could possibly occur by using numpy instead of arrays/lists

Author: Nicholas Fong
        Lawrence Berkeley National Laboratory
        National Energy Research Scientific Computing Center

Acknowledgment:
        This work was supported by the Director, Office of Science,
        Division of Mathematical, Information, and Computational
        Sciences of the U.S. Department of Energy under contract
        DE-AC02-05CH11231, using resources of the National Energy Research
        Scientific Computing Center.
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
import time
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler
from mpi4py import MPI as mpi
import subprocess
import os

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
parser.add_argument("-f", "--force", type=float,
        help = "force constant")
args = parser.parse_args()

params.num_particles = args.numparticles if args.numparticles else 100
params.simulation_height = args.height if args.height else 1000
params.simulation_width = args.width if args.width else 1000
params.simulation_depth = args.depth if args.depth else 1000
params.dt = args.dt if args.dt else 0.0005
#params.force = args.force if args.force else 100
params.force = args.force if args.force else 100000
params.num_active_workers = 0
params.new_num_active_workers = 0
params.partitions = {}
params.max_radius = min(params.simulation_width, params.simulation_height, params.simulation_depth)//32
params.timesteps_per_second = 0
params.init_total_energy = 0.0
params.curr_total_energy = 0.0

if params.rank is 0:
    # Create partitions 1 through params.num_threads - 1
    for i in range(1, params.num_threads):
        params.partitions[i] = Partition(i)

    # Create Particles for Partitions
    for i in range(params.num_particles):
        radius = 30#random.randint(1, params.max_radius)
        position = [random.randint(radius, params.simulation_width - 1),
                    random.randint(radius, params.simulation_height - 1),
                    random.randint(radius, params.simulation_depth - 1)]
        velocity = [400*random.randint(0,radius//4),
                    400*random.randint(0,radius//4),
                    400*random.randint(0,radius//4)]
        mass = 3#random.randint(1,10)
        params.init_total_energy += 0.5 * mass * (velocity[0]**2 + velocity[1]**2 + velocity[2]**2)
        thread_num = util.determine_particle_thread_num(position[0])
        new_particle = Particle(i, thread_num, position, velocity, mass, radius)
        params.partitions[thread_num].add_particle(new_particle)

    params.curr_total_energy = params.init_total_energy

def update_params():
    params.new_num_active_workers = params.comm.bcast(params.new_num_active_workers)

# Broadcast setup information
params.partitions = params.comm.bcast(params.partitions)
params.num_active_workers = params.comm.bcast(params.num_active_workers)
update_params()

colors = {
    0: "255,255,255",

    1: "255,000,000",
    2: "255,102,000",
    3: "255,204,000",
    4: "204,255,000",
    5: "102,255,000",

    6: "000,255,000",
    7: "000,255,102",
    8: "000,255,204",
    9: "000,204,255",
    10: "000,102,255",

    11: "000,000,255",
    12: "102,000,255",
    13: "204,000,255",
    14: "255,000,204",
    15: "255,000,102",
}
num_colors = len(colors)

FNULL = open(os.devnull, 'w')

# One timestep
def timestep():
    """Only do something as a slave if an active worker"""
    if params.rank is 0:
#        threading.Thread(target=subprocess.call(["blink1-tool", "--rgb=" + str(colors[params.rank%4]), "--blink=1", "-m0", "-t20"],stdout=FNULL, stderr=subprocess.STDOUT)).start()
        subprocess.Popen(["blink1-tool --rgb=" + str(colors[0]) + " --blink=1, -m0, -t20 > /dev/null"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        for i in range(1, params.num_active_workers+1):
            new_particles = params.comm.recv(source = mpi.ANY_SOURCE, status = params.mpi_status, tag = 0)
            params.partitions[params.mpi_status.Get_source()].particles = new_particles
    elif params.rank <= params.num_active_workers:
        subprocess.Popen(["blink1-tool --rgb=" + str(colors[params.rank % num_colors]) + " --blink=5, -m0, -t20 > /dev/null"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        partition = params.partitions[params.rank]
        partition.send_and_receive_neighboring_particles()
        partition.interact_particles()
        partition.exchange_particles()
        partition.update_master()

def change_num_active_workers():
    params.num_active_workers = params.new_num_active_workers
    print("In change num_active_workers "+str(params.rank)+" "+str(params.num_active_workers))
    if params.rank is 0:
        if params.new_num_active_workers < 1 or params.new_num_active_workers > params.num_threads - 1:
            util.debug("Invalid number of active workers requested: " + params.new_num_active_workers)

        new_distribution = {}
        for i in range(1, params.num_threads):
            new_distribution[i] = set()

        for partition_id, partition in params.partitions.items():
            for particle in partition.particles:
                new_thread = util.determine_particle_thread_num(particle.position[0])
                particle.thread_num = new_thread
                new_distribution[new_thread].add(particle)

        for i in range(1, params.num_threads):
            print("sending "+str(i))
            params.partitions[i].particles = new_distribution[i]
            params.comm.send(new_distribution[i], dest = i, tag = 11)
    else:
        print("receiving "+str(params.rank))
        params.partitions[params.rank].receive_new_particles()
        #print("received "+str(params.rank))

endpoint = "{\n}"
class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to the API endpoint"""
        global endpoint
        parsed_path = urlparse(self.path)
        if "/api/v1/get_particles" in parsed_path:
            message = endpoint
            self.send_response(200)
            # TODO: Security?
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        else:
            util.info("GET sent to " + str(parsed_path[2]))

    def do_POST(self):
        """Handle POST requests to the API endpoint"""
        global endpoint
        parsed_path = urlparse(self.path)
        if "/api/v1/post_parameters" in parsed_path:
            self.send_response(200)
            # TODO: Security?
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(length).decode("utf-8")
            #post_data = self.rfile.read(length)
            # Parse data from POST
            print('Got a post ')
            print(type(post_data))
            print(post_data)
            new_data = parse_qs(post_data)
            print(type(new_data))
            for x in new_data:
               print(x)
               print(new_data[x])
            params.new_num_active_workers = int(new_data['num_workers'][0])
            #change_num_active_workers()
        else:
            util.info("POST sent to " + str(parsed_path[2]))
    def log_message(self, format, *args):
        return

def main():
    global endpoint

    if params.rank is 0:
        from http.server import HTTPServer
        port_number = 8080
        host = "10.0.0.101"
        server = HTTPServer((host, port_number), Server)
        util.info("Starting server on port " +  str(port_number) + ", ^c to exit")
        threading.Thread(target=server.serve_forever).start()

    iterations = 0
    while True:
        # Timing
        samples = 100
        iterations += 1

        if (iterations % samples == 1) and params.rank == 0:
            start = time.time()

        # Any Changes to number of workers?
        update_params()
        if params.new_num_active_workers is not params.num_active_workers:
            change_num_active_workers()

        timestep()

        # Timing
        if (iterations % samples == 0) and params.rank == 0:
            params.timesteps_per_second = samples/(time.time() - start)
#            util.info(str(params.partitions))
#            util.info("Average steps per second: " + str(params.timesteps_per_second))

        if params.rank is 0:
            # Use a copy of endpoint to prevent queries to endpoint from
            # receiving an in-progress timestep
            temp_endpoint =   "{\n"
            param_endpoint =  "    \"params\": {\n"
            param_endpoint += "        \"num_particles\": " + str(params.num_particles) + ",\n"
            param_endpoint += "        \"num_active_workers\": " + str(params.num_active_workers) + ",\n"
            param_endpoint += "        \"simulation_height\": " + str(params.simulation_height) + ",\n"
            param_endpoint += "        \"simulation_width\": " + str(params.simulation_width) + ",\n"
            param_endpoint += "        \"simulation_depth\": " + str(params.simulation_depth) + ",\n"
            param_endpoint += "        \"timesteps_per_second\": " + str(params.timesteps_per_second) + ",\n"
            param_endpoint += "        \"total_energy\": " + str(params.curr_total_energy) + "\n"
            param_endpoint += "    },\n"

            params.curr_total_energy = 0.0

            particles_endpoint = "    \"particles\": [\n"
            for key, partition in params.partitions.items():
                for particle in partition.particles:
#                    particle.neighbors = ""
#                    particles_endpoint += particle.jsonify()#json.dumps(particle, default=lambda obj: obj.__dict__, sort_keys = True, indent=4) + ",\n"
                    particles_endpoint += particle.jsonify()#json.dumps(particle, default=lambda obj: obj.__dict__, sort_keys = True, indent=4) + ",\n"
                    params.curr_total_energy += 0.5 * particle.mass * (particle.velocity[0]**2 + particle.velocity[1]**2 + particle.velocity[2]**2)
            particles_endpoint = particles_endpoint[:-2] # trim extra comma

            util.debug('init_total_energy_______: ' + str(params.init_total_energy))

            if True:
#            if not iterations % 1000:
                sqrt_ratio = math.sqrt(params.init_total_energy / params.curr_total_energy)
#                ratio = params.init_total_energy / params.curr_total_energy
                for key, partition in params.partitions.items():
                    for particle in partition.particles:
                        for i in range(3):
                            particle.velocity[i] *= sqrt_ratio
                    params.comm.send(partition.particles, dest=partition.thread_num, tag=99)
                util.debug('curr_total_energy_before: ' + str(params.curr_total_energy))

            # RM
            if True:
                params.curr_total_energy = 0.0
#            if not iterations % 1000:
                for key, partition in params.partitions.items():
                    for particle in partition.particles:
                        params.curr_total_energy += 0.5 * particle.mass * (particle.velocity[0]**2 + particle.velocity[1]**2 + particle.velocity[2]**2)
                util.debug('curr_total_energy_after_: ' + str(params.curr_total_energy))
            # RM

            endpoint = "{\n" + param_endpoint + particles_endpoint + "\n    ]\n}\n"
#        elif not iterations % 1000:
        else:
            new_particles = params.comm.recv(source=0, status=params.mpi_status, tag=99)
            params.partitions[params.rank].set_particles(new_particles)

if __name__ == "__main__":
    main()
