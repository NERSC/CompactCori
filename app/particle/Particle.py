#!/usr/bin/python
"""
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

import util
import params
import math

class Particle:
    """Particle class for MD simulation."""

    def __init__(self, particle_id, thread_num, position, velocity, mass,
            radius):
        util.validate_list(position, velocity)
        util.validate_int(particle_id, thread_num, mass, radius)

        self.particle_id = particle_id
        self.thread_num = thread_num
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.radius = radius
        self.neighbors = None
        util.debug("I am a particle at " + str(self.position) + " and I am owned by " + str(self.thread_num))

    def jsonify(self):
        """Hacky conversion to JSON to avoid infinite loop with jsonify and
        nested neighbors
        """
        json =  "        {\n"
        json += "            \"particle_id\": " + str(self.particle_id) + ",\n"
        json += "            \"thread_num\": " + str(self.thread_num) + ",\n"
        json += "            \"position\": " + str(self.position) + ",\n"
        json += "            \"velocity\": " + str(self.velocity) + ",\n"
        json += "            \"mass\": " + str(self.mass) + ",\n"
        json += "            \"radius\": " + str(self.radius) + "\n"
        json += "        },\n"
        return json

    def euclidean_distance_to(self, particle):
        x = abs(self.position[0] - particle.position[0])
        y = abs(self.position[1] - particle.position[1])
        z = abs(self.position[2] - particle.position[2])
        center_to_center = math.sqrt((x**2) + (y**2) + (z**2))
        return (center_to_center - self.radius - particle.radius, (x, y, z))

    def populate_neighbors(self, particles):
        self.neighbors = []
        for particle in particles:
            euclidean_distance, distances = self.euclidean_distance_to(particle)
            if euclidean_distance <= 0 and particle is not self:
                self.neighbors.append((particle, distances))
        if len(self.neighbors) > 1:
            util.debug("There are multiple collisions happening at once")

    def get_momentum(self):
        return tuple([velocity * self.mass for velocity in self.velocity])

    def update_velocity(self):
        collision_mass = 0
        collision_velocity = [0, 0, 0]            # The velocity of the entire system that's colliding
        for neighbor, distances in self.neighbors:
            collision_mass += neighbor.mass
            for i in range(3):
                collision_velocity[i] += neighbor.velocity[i]

        mass_difference = self.mass - collision_mass
        mass_sum = self.mass + collision_mass
        for i in range(3):
            self.velocity[i] = (mass_difference/mass_sum) * self.velocity[i] +\
                    ((2*collision_mass)/mass_sum)*collision_velocity[i]

    def update_position(self, time):
        delta = [component*time for component in self.velocity]
#        util.info("Delta is " + str(delta))
        self.position[0] += delta[0]
        self.position[1] += delta[1]
        self.position[2] += delta[2]

        if any(d > self.radius for d in delta):
            util.debug("A particle is moving a distance of more than self.radius")

        # Bounce particles off edge of simulation
        simulation = [params.simulation_width, params.simulation_height, params.simulation_depth]
        for i in range(3):
            while self.position[i] < 0 or self.position[i] > simulation[i]:
                util.debug("I am out of bounds: " + str(self.position) + " and I am going this fast:" + str(self.velocity))
                self.velocity[i] *= -1
                self.position[i] = self.position[i]*-1 if self.position[i] < 0\
                    else 2*simulation[i] - self.position[i]
#            util.debug("I am no longer out of bounds: " + str(self.position))
#        util.info("Particle " + str(self.particle_id) + " with mass " + str(self.mass) + " is at " + str(self.position))
