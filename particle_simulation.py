#!/usr/bin/python
"""
A parallelized MD simulation in Python written for version 1 of the Compact Cory
project at NERSC.

This runs in O(n^2) time since all particles are compared to one another when
locating in-range neighbors.
"""
import argparse
import random
import math

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
parser.add_argument("-d", "--dt", type=int,
        help = "multiplier time constant")
args = parser.parse_args()

num_particles = args.numparticles if args.numparticles else 20
interaction_radius = args.radius if args.radius else 100
force_amount = args.force if args.force else 50
simulation_height = args.height if args.height else 1000
simulation_width = args.width if args.width else 1000
force_constant = args.force if args.force else 1
dt = args.dt if args.dt else 0.00001

particles = []

class Particle:
    particles = []
    def __init__(self, magnitude = 1, x_velocity = 0, y_velocity = 0):
        self.x_position = random.randint(0, simulation_width)
        self.y_position = random.randint(0, simulation_width)
        self.magnitude = magnitude
        self.neighbors = None
        self.x_force = None
        self.y_force = None
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        particles.append(self)

    def euclidean_distance_to(self, particle):
        x = abs(self.x_position - particle.x_position)
        y = abs(self.y_position - particle.y_position)
        return (math.sqrt(pow(x, 2) + pow(y, 2)), x, y)

    def populate_neighbors(self):
        self.neighbors = []
        for particle in particles:
            euclidean_distance, x_distance, y_distance = self.euclidean_distance_to(particle)
            if euclidean_distance < interaction_radius and particle is not self:
                self.neighbors.append((particle, x_distance, y_distance))

    def calculate_force(self, particle, x_distance, y_distance):
        x = force_constant * (self.magnitude * particle.magnitude)/pow(x_distance, 2) if x_distance else 0
        y = force_constant * (self.magnitude * particle.magnitude)/pow(y_distance, 2) if y_distance else 0
        return x,y

    def calculate_net_force(self):
        self.x_force = 0
        self.y_force = 0
        for neighbor, x_distance, y_distance in self.neighbors:
            x, y = self.calculate_force(neighbor, x_distance, y_distance)
            self.x_force += x
            self.y_force += y

    def update_velocity(self):
        self.x_velocity += self.x_force * dt
        self.y_velocity += self.y_force * dt

    def move_particle(self):
        x_displacement = self.x_velocity * dt
        y_displacement = self.y_velocity * dt

        new_x = self.x_position + x_displacement
        new_y = self.y_position + y_displacement

        # Bounce the particle against the walls
        if new_x < 0:
            self.x_velocity *= -1
            self.x_position = x_displacement- self.x_position
        elif new_x > simulation_width:
            self.x_velocity *= -1
            self.x_position = x_displacement- self.x_position
        else:
            self.x_position = new_x

        if new_y < 0:
            self.y_velocity *= -1
            self.y_position = y_displacement - self.y_position
        elif new_y > simulation_width:
            self.y_velocity *= -1
            self.y_position = y_displacement - self.y_position
        else:
            self.y_position = new_y

    def __str__(self):
        if self.neighbors:
            return "Currently located at: (" + str(self.x_position) + "," + str(self.y_position) + ") with " + str(len(self.neighbors)) + " neighbors"
        else:
            return "Currently located at: (" + str(self.x_position) + "," + str(self.y_position) + ") with " + str(self.neighbors) + " neighbors"


# Create Particlesj
for _ in range(num_particles):
    Particle()

# One timestep
def timestep():
    for particle in particles:
        particle.populate_neighbors()
    for particle in particles:
        particle.calculate_net_force()
    for particle in particles:
        particle.update_velocity()
    for particle in particles:
        particle.move_particle()

# Run simulation
#while True:
for i in range(3):
    print('\n')
    print(*particles, sep='\n')
    timestep()

