#!/usr/bin/python
"""
A parallelized MD simulation in Python written for version 1 of the Compact Cory
project at NERSC.

    num_particles
    step_size
    interaction_radius
    force_amount
    particle_type
    simulation_width
    simulation_height
    initial_distribution
"""
import argparse
import random
import math

# TODO add argparse.

### Temporary vars:
num_particles = 20
interaction_radius = 10
force_amount = 50
simulation_width = 1000
simulation_height = 1000
### End temporary vars

FORCE_CONSTANT = 1
particles = None

class Particle:
    def __init__(self, magnitude = 1):
        self.x_position = random.randint(0, simulation_width)
        self.y_position = random.randint(0, simulation_width)
        self.magnitude = magnitude
        self.neighbors = None
        self.x_force = None
        self.y_force = None
        self.particles = particles

    def euclidean_distance_to(self, particle):
        x = abs(self.x_position - particle.x_position)
        y = abs(self.y_position - particle.y_position)
        return (math.sqrt(pow(x, 2) + pow(y, 2)), x, y)

    def populate_neighbors(self):
        self.neighbors = []
        for particle in particles:
            euclidean_distance, x_distance, y_distance = self.euclidean_distance_to(particle)
            if euclidean_distance < interaction_radius:
                self.neighbors.append((particle, x_distance, y_distance))

    def calcaulate_force(self, particle, x_distance, y_distance):
        x =  FORCE_CONSTANT * (self.magnitude * particle.magnitude)/pow(x_distance, 2)
        y =  FORCE_CONSTANT * (self.magnitude * particle.magnitude)/pow(y_distance, 2)
        return x,y

    def calculate_net_force(self):
        telf.x_force = 0
        self.y_force = 0
        for neighbor, x_distance, y_distance in self.neighbors:
            x, y = calculate_force(neighbor, x_distance, y_distance)
            self.x_force += x
            self.y_force += y

    def move_particle(self):
        self.x_position += self.x_force
        self.y_position += self.y_force

    def __str__(self):
        return "Currently located at: (" + str(self.x_position) + "," + str(self.y_position) + ") with " + str(self.neighbors) + "neighbors"


# Create Particles
particles = [Particle() for particle in range(num_particles)]

# Run simulation
while True:
    print(*particles, sep='\n')
    map(lambda particle: particle.populate_neighbors(), particles)
    map(lambda particle: particle.calculate_net_force(), particles)
    map(lambda particle: particle.move_particles(), particles)

