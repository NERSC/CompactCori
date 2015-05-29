#!/usr/bin/python
"""
A parallelized MD simulation in Python written for version 1 of the Compact Cory
project at NERSC.
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
args = parser.parse_args()

num_particles = args.numparticles if args.numparticles else 20
interaction_radius = args.radius if args.radius else 10
force_amount = args.force if args.force else 50
simulation_height = args.height if args.height else 1000
simulation_width = args.width if args.width else 1000
force_constant = args.force if args.force else 1

particles = []

class Particle:
    particles = []
    def __init__(self, magnitude = 1):
        self.x_position = random.randint(0, simulation_width)
        self.y_position = random.randint(0, simulation_width)
        self.magnitude = magnitude
        self.neighbors = None
        self.x_force = None
        self.y_force = None
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

    def move_particle(self):
        self.x_position += self.x_force
        self.y_position += self.y_force

    def __str__(self):
        if self.neighbors:
            return "Currently located at: (" + str(self.x_position) + "," + str(self.y_position) + ") with " + str(len(self.neighbors)) + " neighbors"
        else:
            return "Currently located at: (" + str(self.x_position) + "," + str(self.y_position) + ") with " + str(self.neighbors) + " neighbors"


# Create Particles
for _ in range(num_particles):
    Particle()

# Run simulation
while True:
    print('\n')
    print(*particles, sep='\n')
    for particle in particles:
        particle.populate_neighbors()
    for particle in particles:
        particle.calculate_net_force()
    for particle in particles:
        particle.move_particle()

