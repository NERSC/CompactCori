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
import urlparse
import json
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
parser.add_argument("-f", "--force", type=int,
        help = "force between particles")
parser.add_argument("--height", type=int,
        help = "height of simulation window")
parser.add_argument("--width", type=int,
        help = "width of simulation window")
parser.add_argument("-d", "--dt", type=float,
        help = "multiplier time constant")
parser.add_argument("-a", "--print_ascii", action="store_true",
        help = "output print_ascii of simulation to STDOUT")
parser.add_argument("-s", "--serial", action="store_true",
        help = "specifies if simulation should be run serially")

args = parser.parse_args()

num_particles = args.numparticles if args.numparticles else 20
radius = args.radius if args.radius else 100
force_amount = args.force if args.force else 50
simulation_height = args.height if args.height else 1000
simulation_width = args.width if args.width else 1000
force_constant = args.force if args.force else 1
dt = args.dt if args.dt else 0.0005
print_ascii = True if args.print_ascii else False

particles = []

# TODO: Remove typechecking for production
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
    """
    Partition class, where each Partition corresponds to the area of the
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

class Particle:
    static_particles = particles
    def __init__(self, particle_id, thread_num, position, velocity, mass,
                radius):
        # TODO: Add validation of list length
        validate_list(position, velocity)
        validate_int(particle_id, thread_num, mass, radius)

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
        midpoint_distance = math.sqrt((x**2) + (y**2) + (z**2))
        return (midpoint_distance - self.radius - particle.radius, (x, y, z))

    def populate_neighbors(self):
        self.neighbors = []
        for particle in Particle.static_particles:
            euclidean_distance, distances = self.euclidean_distance_to(particle)
            if euclidean_distance < self.radius and particle is not self:
                self.neighbors.append((particle, distances))

    def get_momentum(self):
        return tuple([velocity * self.mass for velocity in self.velocity])

    def update_velocity(self, time):
        collision_momentum = [0, 0, 0]            # The momentum of the entire system that's colliding
        collision_momentum = self.get_momentum()  # The momentum of the entire system that's colliding
        for neighbor in self.neighbors:
            neighbor_momentum = neighbors.get_momentum()
            collision_momentum[0] += neighbor_momentum[0]
            collision_momentum[1] += neighbor_momentum[1]
            collision_momentum[2] += neighbor_momentum[2]


#    def calculate_force(self, particle, distance):
#        x = force_constant * (self.mass * particle.mass)/(distance[0]**2) if distance[0] else 0
#        y = force_constant * (self.mass * particle.mass)/(distance[1]**2) if distance[1] else 0
#        z = force_constant * (self.mass * particle.mass)/(distance[2]**2) if distance[2] else 0
#        return (x,y,z)
#
#    def calculate_net_force(self):
#        for neighbor, distance in self.neighbors:
#            x, y, z = self.calculate_force(neighbor, x_distance, y_distance)
#            # DO AN UPDATE HERE
#
#    def move_particle(self):
#        """
#        Naively assumes velocity is less than the size of the simulation window
#        """
#        self.x_velocity += self.x_accel * dt
#        self.y_velocity += self.y_accel * dt
#
#        self.x_position += self.x_velocity * dt
#        self.y_position += self.y_velocity * dt
#
#        while self.x_position < 0 or self.x_position > simulation_width:
#            self.x_velocity *= -1
#            self.x_position = self.x_position*-1 if self.x_position < 0\
#                else 2*simulation_width - self.x_position
#
#        while self.y_position < 0 or self.y_position > simulation_height:
#            self.y_velocity *= -1
#            self.y_position = self.y_position*-1 if self.y_position < 0\
#                else 2*simulation_height - self.y_position
#
#        self.x_position = int(self.x_position)
#        self.y_position = int(self.y_position)

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

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests to the API endpoint
        """
        parsed_path = urlparse.urlparse(self.path)
        if "/api/v1/get_particles" in parsed_path:
            message = "\r\n".join(endpoint)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(message)
        else:
            pass

    def do_POST(self):
        """
        Handle POST requests to the API endpoint
        """
        parsed_path = urlparse.urlparse(self.path)
        if "/api/v1/post_parameters" in parsed_path:
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length).decode('utf-8')
            # Parse data from POST
#            # Print for debugging
#            self.wfile.write(str(post_data).encode("utf-8"))
#            self.wfile.write("\n".encode("utf-8"))
        else:
            pass

endpoint = "{}"
def main():
    from http.server import HTTPServer
    server = HTTPServer(('127.0.0.1', 8080), Server)
    print("Starting server, ^c to exit")
    server.serve_forever()
    for i in range(300):
        timestep()
        if print_ascii:
            text_simulation()
        else:
            # Use a copy of endpoint to prevent queries to endpoint from
            # receiving an in-progress timestep
            temp_endpoint = "{\n"
            for particle in particles:
                temp_endpoint += json.dumps(particle, default=lambda obj: obj.__dict__, sort_keys = True, indent=2)
            temp_endpoint += "\n}"
            endpoint = temp_endpoint

if __name__ == "__main__":
    main()
