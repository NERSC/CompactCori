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

    def jsonify(self, indent = 4):
        """Hacky conversion to JSON to avoid infinite loop with jsonify and
        nested neighbors
        """
##       TODO: Debug this to DRY out this method
#        particle_dict = self.__dict__
#        util.info("Dict looks like: " + str(particle_dict))
#        json = json.dumps(particle_dict, sort_keys = True, indent=4)
##        json = json.dumps(particle_dict, default=lambda obj: obj.__dict__, sort_keys = True, indent=4)
#        util.info("And now it looks like: " + str(json))
#        json = "\n".join((" " * indent) + i for i in json.splitlines())

        json =  " " * indent + "{\n"
        json += " " * 2 * indent + "\"particle_id\": " + str(self.particle_id) + ",\n"
        json += " " * 2 * indent + "\"thread_num\": " + str(self.thread_num) + ",\n"
        json += " " * 2 * indent + "\"position\": " + str(self.position) + ",\n"
        json += " " * 2 * indent + "\"velocity\": " + str(self.velocity) + ",\n"
        json += " " * 2 * indent + "\"mass\": " + str(self.mass) + ",\n"
        json += " " * 2 * indent + "\"radius\": " + str(self.radius) + "\n"
        json += " " * indent + "},\n"
        return json

    def euclidean_distance_to(self, particle):
        """Return the 3D euclidean distance between this Particle and another"""
        x = self.position[0] - particle.position[0]
        y = self.position[1] - particle.position[1]
        z = self.position[2] - particle.position[2]
        center_to_center = math.sqrt((x**2) + (y**2) + (z**2))
        #return (center_to_center - self.radius - particle.radius, (x, y, z))
        return (center_to_center, (x, y, z))

    def update_velocity(self, particles):
        """Populate the list of neighbors with particles that are colliding this
        particle
        """
        neighbors = []
        for particle in particles:
            euclidean_distance, distances = self.euclidean_distance_to(particle)
            #if euclidean_distance <= 0 and particle is not self:
            if euclidean_distance <= 5*(self.radius + particle.radius) and particle is not self:
                neighbors.append((particle, distances, euclidean_distance))

        #p_energy = 0
        max_force = 5000
        for neighbor, distances, euclidean_distance in neighbors:
            #p_energy = p_energy + 5000 *( ( 1 / euclidean_distance ) - (1 / (5*(self.radius + particle.radius) ) )
            for i in range(3):
                #max_force = 10
                if euclidean_distance == 0:
                    force = max_force
                else:
                    force = params.force * (1 * (distances[i])/euclidean_distance**3)/self.mass
                if force > max_force:
                    force = max_force
                elif force < -1*max_force:
                    force = -1*max_force
                self.velocity[i] += force

    def update_position(self, time):
        """Update the position of this Particle based on the velocity of the
        Particle
        """
        delta = [component*time for component in self.velocity]
#        util.info("Delta is " + str(delta))
        self.position[0] += delta[0]
        self.position[1] += delta[1]
        self.position[2] += delta[2]

        if any(d > self.radius for d in delta):
            util.debug(str(self.particle_id) + " is moving a distance of more than self.radius")
            self.velocity[0] = self.velocity[0]/2
            self.velocity[1] = self.velocity[1]/2
            self.velocity[2] = self.velocity[2]/2

        # Bounce particles off edge of simulation
        simulation = [params.simulation_width, params.simulation_height, params.simulation_depth]
        for i in range(3):
            while self.position[i] < 0 or self.position[i]  > simulation[i]:
#                util.debug(str(self.particle_id) + " is out of bounds: " + str(self.position) + " and is going this fast:" + str(self.velocity))
                self.velocity[i] *= -1
                self.position[i] = self.position[i]*-1 if self.position[i] < 0\
                    else 2*simulation[i] - self.position[i]
#            util.debug("I am no longer out of bounds: " + str(self.position))
#        util.info("Particle " + str(self.particle_id) + " with mass " + str(self.mass) + " is at " + str(self.position))
#        util.info("Particle " + str(self.particle_id) + " is moving: " + str(self.velocity))
