#!/usr/bin/python
"""
A parallelized MD simulation in Python written for version 1 of the Compact Cori
project at NERSC.

This runs in O(n^2) time since all particles are compared to one another when
locating in-range neighbors.

Threads in mpi4py are 0-indexed
"""
import argparse
import random
import math
import numpy as np
from mpi4py import MPI as mpi
import json
from http.server import BaseHTTPRequestHandler
import urlparse

comm = mpi.COMM_WORLD
rank = comm.Get_rank()
num_threads = comm.Get_size()

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--numparticles", type=int,
        help = "number of particles in simulation")
parser.add_argument("-r", "--radius", type=int,
        help = "radius of particle interaction")
parser.add_argument("-f", "--force", type=int,
        help = "force between particles")
parser.add_argument("--height", type=int,
        help = "height of simulation window")
parser.add_argument("--width", type=int,
        help = "width of simulation window")
parser.add_argument("-d", "--dt", type=float,
        help = "multiplier time constant")
parser.add_argument("-a", "--ascii", action="store_true",
        help = "output ascii of simulation to STDOUT")
parser.add_argument("-s", "--serial", action="store_true",
        help = "specifies if simulation should be run serially")

args = parser.parse_args()

num_particles = args.numparticles if args.numparticles else 20
interaction_radius = args.radius if args.radius else 100
force_amount = args.force if args.force else 50
simulation_height = args.height if args.height else 1000
simulation_width = args.width if args.width else 1000
force_constant = args.force if args.force else 1
dt = args.dt if args.dt else 0.0005
ascii = True if args.ascii else False

particles = []

# DRY out typechecking of arguments
def validate_int(*args):
    for arg in args:
        if type(arg) is not int:
            raise ArgumentError("incorrect type argument: " + type(arg) +
                    " was passed instead of an int")

def validate_list(*args):
    for arg in args:
        if type(arg) is not list:
            raise ArgumentError("incorrect type argument: " + type(arg) +
                    " was passed instead of a list")

def validate_dict(*args):
    for arg in args:
        if type(arg) is not dict:
            raise ArgumentError("incorrect type argument: " + type(arg) +
                    " was passed instead of a dict")

def validate_particle_set(*args):
    for arg in args:
        if type(arg) is not set:
            raise ArgumentError("incorrect type argument: " + type(arg) +
                    " was passed instead of a set")
        for obj in arg:
            if type(obj) is not Particle:
                raise ArgumentError("Non-particle type in set; received a "
                        + type(obj) + " instead of a Particle")

class Partition:
    def __init__(self, thread_num):
        validate_int(thread_num)
        self.thread_num = thread_num
        self.delta_x = simulation_width//num_threads
        self.start_x = self.delta_x*self.thread_num
        self.end_x = self.start_x + delta_x
        self.active = True

    def update_neighbor_thread_list():
        num_neighbor_partitions = math.ceil(interaction_radius/self.delta_x)
        lower_threads = [ i for i in range(max(0,self.thread_num -
            num_neighbor_partitions), self.thread_num)]
        upper_threads = [ i for i in range(self.thread_num + 1,
            min(self.thread_num + num_neighbor_partitions + 1, num_threads)]
        self.neighbor_threads = lower_threads + upper_threads

    def add_particles(particle_set):
        validate_particle_set(particle_set)
        self.particles.union(particle_set)

    def remove_particles(particle_set):
        validate_particle_set(particle_set)
        self.particles.difference_update(particle_set)

    def set_particles(particle_set):
        validate_particle_set(particle_set)
        self.particles = particle_set

class Particle:
    static_particles = particles
    def __init__(self, thread_num = 0, x_position = None, y_position = None,
        x_velocity = 0, y_velocity = 0, mass = 1):
        self.x_position = x_position if (x_position != None)\
            else random.randint(0, simulation_width - 1)
        self.y_position = y_position if (y_position != None)\
            else random.randint(0, simulation_height - 1)
        self.x_velocity = x_velocity if (x_velocity != None)\
            else random.randint(-1*simulation_height//10, simulation_height//10)
        self.y_velocity = y_velocity if (y_velocity != None)\
            else random.randint(-1*simulation_height//10, simulation_height//10)
        self.mass = mass
        self.neighbors = None
        self.x_accel = 0    # rm
        self.y_accel = 0    # rm
        self.thread_num = thread_num

    def euclidean_distance_to(self, particle):
        x = abs(self.x_position - particle.x_position)
        y = abs(self.y_position - particle.y_position)
        return (math.sqrt((x**2) + (y**2)), x, y)

    def populate_neighbors(self):
        self.neighbors = []
        for particle in Particle.static_particles:
            euclidean_distance, x_distance, y_distance = self.euclidean_distance_to(particle)
            if euclidean_distance < interaction_radius and particle is not self:
                self.neighbors.append((particle, x_distance, y_distance))

    def calculate_force(self, particle, x_distance, y_distance):
        x = force_constant * (self.mass * particle.mass)/(x_distance**2) if x_distance else 0
        y = force_constant * (self.mass * particle.mass)/(y_distance**2) if y_distance else 0
        return x,y

    def calculate_net_force(self):
        self.x_accel = 0
        self.y_accel = 0
        for neighbor, x_distance, y_distance in self.neighbors:
            x, y = self.calculate_force(neighbor, x_distance, y_distance)
            self.x_accel += x * x_distance
            self.y_accel += y * y_distance

    def move_particle(self):
        """
        Naively assumes velocity is less than the size of the simulation window
        """
        self.x_velocity += self.x_accel * dt
        self.y_velocity += self.y_accel * dt

        self.x_position += self.x_velocity * dt
        self.y_position += self.y_velocity * dt

        while self.x_position < 0 or self.x_position > simulation_width:
            self.x_velocity *= -1
            self.x_position = self.x_position*-1 if self.x_position < 0\
                else 2*simulation_width - self.x_position

        while self.y_position < 0 or self.y_position > simulation_height:
            self.y_velocity *= -1
            self.y_position = self.y_position*-1 if self.y_position < 0\
                else 2*simulation_height - self.y_position

        self.x_position = int(self.x_position)
        self.y_position = int(self.y_position)

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

def enable_partition(partition):
    if type(partition) is not Partition:
        raise TypeError("A " + type(partition) + " was passed to disable_partition")
    partition.active = True

# Create Partitions and set neighbors
partitions = []
for i in range(num_threads):
    partitions.append(Partition(i))

# Create Particles for Parallel Processes
for _ in range(num_particles):
    curr_particle = Particle()

    particles.append(Particle())

def text_simulation():
    """
    Print out an ASCII-based representation of the simulation to STDOUT
    """
    # Populate nested list
    arr = [[" "] * simulation_height for _ in range(simulation_width)]
    for particle in particles:
        arr[particle.x_position][particle.y_position] = "o"

    # Convert list to buffer to print to STDOUT
    buf = " "
    for i in range(simulation_width):
        buf += str(i % 10)
    buf += "\n " + "-" * simulation_width + "\n"
    for j in range(simulation_height):
        buf += "|"
        for i in range(simulation_width):
            buf += arr[i][j]
        buf += "|" +  str(j) + "\n"
    buf += " " + "-" * simulation_width
    print(buf)

# One timestep
def timestep():
    for particle in particles:
        particle.populate_neighbors()
    for particle in particles:
        particle.calculate_net_force()
    for particle in particles:
        particle.move_particle()

endpoint = "{}"
def main():
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('localhost', 8080), GetHandler)
    print("Starting server, ^c to exit")
    server.serve_forever()
    for i in range(300):
        timestep()
        if ascii:
            text_simulation()
        else:
            # Use a temporary endpoint so queries to endpoint only return data
            # from a completed timestep
            temp_endpoint = "{\n"
            for particle in particles:
                temp_endpoint += json.dumps(particle, default=lambda obj: obj.__dict__, sort_keys = True, indent=2)
            temp_endpoint += "\n}"
            endpoint = temp_endpoint

class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests to the API endpoint
        """
        message = "\r\n".join(endpoint)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

#class PostHandler(BaseHTTPRequestHandler):
#    def do_POST(self):
#        """
#        Handle POST requests to the API endpoint
#        """
#        message = "\r\n".join(endpoint)
#        self.send_response(200)
#        self.end_headers()
#        self.wfile.write(message)
#        return

if __name__ == "__main__":
    main()
