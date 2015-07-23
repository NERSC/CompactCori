#!/usr/bin/python

import util
import params

class Partition:
    """Partition class, where each Partition corresponds to the area of the
    simulation that a thread owns.

    Invariant: If Partition i is active (that is, if there are i threads working
    on the simulation), then for all partitions j < i, j is active as well
    """
    partitions = {}
    def __init__(self, thread_num):
        util.validate_int(thread_num)

        self.thread_num = thread_num
        self.particles = set()
        self.previous_neighbor_particles = set()
        self.next_neighbor_particles = set()
        self.delta_x = simulation_width//num_threads
        self.start_x = self.delta_x*self.thread_num
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + delta_x

        # Add self to global list of partitions
        # Consider changing to global params instead of static
        Partition.partitions[self.thread_num] = self
        Partition.num_active_workers += 1

    def add_particles(self, particle_set):
        util.validate_particle_set(particle_set)
        for particle in particle_set:
            particle.thread_num = self.thread_num
        self.particles.union(particle_set)
    
    def add_particle(self, particle):
        self.particles.add(particle)

    def remove_particles(self, particle_set):
        util.validate_particle_set(particle_set)
        self.particles.difference_update(particle_set)

    def set_particles(self, particle_set):
        util.validate_particle_set(particle_set)
        for particle in particle_set:
            particle.thread_num = self.thread_num
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

    def handoff_neighboring_particles(self):
        right = set()
        left = set()
        for particle in self.particles:
            if particle.position[0] + particle.radius + params.max_radius > self.end_x:
                right.add(particle)
            elif particle.position[0] - particle.radius - params.max_radius < self.start_x:
                left.add(particle)
        return (right, left)

    def previous_partition_is_active(self):
        return self.thread_num > 0 and self.thread_num - 1 <= Partition.num_active_workers

    def next_partition_is_active(self):
        return self.thread_num + 1 <= Partition.num_active_workers

