#!/usr/bin/python
"""A parallelized MD simulation in Python written for version 1 of the Compact Cori
project at NERSC.

This runs in O(n^2) time since all particles are compared to one another when
locating in-range neighbors.

Threads in mpi4py are 0-indexed
"""
import argparse
import random
import math
import numpy as np
import json
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler
from mpi4py import MPI as mpi

comm = mpi.COMM_WORLD
rank = comm.Get_rank()
num_threads = comm.Get_size()

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

class Partition:
    """Partition class, where each Partition corresponds to the area of the
    simulation that a thread owns.

    Invariant: If Partition i is active (that is, if there are i threads working
    on the simulation), then for all partitions j < i, j is active as well

    TODO: Ensure that the last partition picks up any coordinates that would
    otherwise be ignored due to floor
    """
    partitions = {}
    def __init__(self, thread_num):
        validate_int(thread_num)

        self.thread_num = thread_num
        self.particles = set()
        self.delta_x = simulation_width//num_threads
        self.start_x = self.delta_x*self.thread_num
        self.end_x = self.start_x + delta_x
        self.active = True
        partitions[thread_num] = self

    def update_neighbor_thread_list(self):
        # If partition 0 and partition 1 is active
        if self.thread_num is 0 and partitions[1].active
            self.neighbor_threads = set(1)
        # If partition 0 and partition 1 is inactive
        elif self.thread_num is 0 and not partitions[1].active:
            self.neighbor_threads = set()
        # If last partition
        elif self.thread_num is num_threads - 1:
            self.neighbor_threads = set(num_threads - 2)
        # If any other partition and the next partition is inactive
        else if not partitions[thread_num + 1].active:
            self.neighbor_threads = set(thread_num - 1)
        # If any other partition and the next partition is active
        else:
            self.neighbor_threads = set(thread_num - 1, thread_num + 1)

    def add_particles(self, particle_set):
        validate_particle_set(particle_set)
        self.particles.union(particle_set)

    def remove_particles(self, particle_set):
        validate_particle_set(particle_set)
        self.particles.difference_update(particle_set)

    def set_particles(self, particle_set):
        validate_particle_set(particle_set)
        self.particles = particle_set

    def is_not_in_range(self, particle):
        """Naively assumes that the particle will never be travelling fast
        enough to jump more than one partition at a time.

        Returns -1 if the particle is in the previous partition
                0 if the particle is still in this partition
                1 if the particle is in the next partition
        """
        if particle.position[0] < self.start_x:
            return -1
        elif particle.position[0] > self.end_x:
            return 1
        else:
            return 0

class Particle:
    def __init__(self, particle_id, thread_num, position, velocity, mass,
                radius):
        # TODO: Add validation of list length
        validate_list(position, velocity)
        validate_int(particle_id, thread_num, mass, radius)
        if radius > min(simulation_width, simulation_height, simulation_depth)/32:
            debug("Radius is greater than 1/32 of the simulation")

        self.particle_id = particle_id
        self.thread_num = thread_num
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.radius = radius
        self.neighbors = None

    def euclidean_distance_to(self, particle):
        x = abs(self.position[0] - particle.position[0])
        y = abs(self.position[1] - particle.position[1])
        z = abs(self.position[2] - particle.position[2])
        center_to_center = math.sqrt((x**2) + (y**2) + (z**2))
        return (center_to_center - self.radius - particle.radius, (x, y, z))

    def populate_neighbors(self, particles):
        self.neighbors = []
        for particle in particles
            euclidean_distance, distances = self.euclidean_distance_to(particle)
            if euclidean_distance < self.radius and particle is not self:
                self.neighbors.append((particle, distances))
        if len(self.neighbors) > 1:
            debug("There are multiple collisions happening at once")

    def get_momentum(self):
        return tuple([velocity * self.mass for velocity in self.velocity])

    def update_velocity(self, time):
        collision_mass = 0
        collision_velocity = [0, 0, 0]            # The velocity of the entire system that's colliding
        for neighbor in self.neighbors:
            collision_mass += neighbor.mass
            for i in range(3):
                collision_velocity[i] += neighbor.velocity[i]

        for i in range 3:
            self.velocity[i] = ((self.mass - collision_mass)/(self.mass +
                    collision.mass)) * self.velocity[i] +
                    2*collision_mass)/(self.mass +
                    collision.mass))*collision_velocity[i]

    def update_position(self, time = dt):
        delta = [component*time for component in self.velocity]
        self.position[0] += delta[0]
        self.position[1] += delta[1]
        self.position[2] += delta[2]

        if any(d > self.radius for d in delta):
            debug("A particle is moving a distance of more than self.radius")

        # Bounce particles off edge of simulation
        for i in range(3):
            while self.position[i] < i or self.position[i] > simulation_width:
                self.velocity[i] *= -1
                self.position[i] = self.position[i]*-1 if self.position[i] < 0\
                    else 2*simulation_width - self.position[i]

    def __repr__(self):
        if self.neighbors:
            return "Currently located at: (" + str(self.x_position) + "," +
                str(self.y_position) + ") with " + str(len(self.neighbors)) +
                " neighbors\n"
        else:
            return "Currently located at: (" + str(self.x_position) + "," +
                str(self.y_position) + ") with " + str(self.neighbors) +
                " neighbors\n"

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
    for particle in particles:
        particle.populate_neighbors()
    for particle in particles:
        particle.calculate_net_force()
    for particle in particles:
        particle.move_particle()

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to the API endpoint"""
        parsed_path = urlparse(self.path)
        if "/api/v1/get_particles" in parsed_path:
            message = "\r\n".join(endpoint)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        else:
            debug("GET request sent to " + parsed_path)

    def do_POST(self):
        """Handle POST requests to the API endpoint"""
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
    from http.server import HTTPServer
    server = HTTPServer(("127.0.0.1", 8080), Server)
    print("Starting server, ^c to exit")
    server.serve_forever()
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
