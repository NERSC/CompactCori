#!/usr/bin/python

class Particle:
    """Particle class for MD simulation."""
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
        self.max_radius = min(simulation_width, simulation_height, simulation_depth)/32

        if radius > self.max_radius;
            debug("Radius is greater than 1/32 of the simulation")

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

    def update_velocity(self):
        collision_mass = 0
        collision_velocity = [0, 0, 0]            # The velocity of the entire system that's colliding
        for neighbor in self.neighbors:
            collision_mass += neighbor.mass
            for i in range(3):
                collision_velocity[i] += neighbor.velocity[i]

        mass_difference = self.mass - collision_mass
        mass_sum = self.mass + collision_mass
        for i in range 3:
            self.velocity[i] = (mass_difference/mass_sum) * self.velocity[i] +\
                    ((2*collision_mass)/mass_sum)*collision_velocity[i]

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
