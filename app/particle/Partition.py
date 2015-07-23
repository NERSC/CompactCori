#!/usr/bin/python

import util
import params

class Partition:
    """Partition class, where each Partition corresponds to the area of the
    simulation that a thread owns.

    Invariant: If Partition i is active (that is, if there are i threads working
    on the simulation), then for all partitions j < i, j is active as well
    """
    def __init__(self, thread_num):
        util.validate_int(thread_num)

        self.thread_num = thread_num
        self.particles = set()
        self.neighbor_particles = set()
        self.delta_x = simulation_width//params.num_threads
        self.start_x = self.delta_x*self.thread_num
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + delta_x

        params.num_active_workers += 1

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

    def send_and_receive_neighboring_particles(self):
        """Send particles that may interact with another partitions particles,
        and receive other partitions' particles that may interact with this
        partition's particles
        """
        right, left = self.handoff()

        # Update neighbors with my particles
        if partition.previous_partition_is_active:
            params.comm.Send(left , dest = rank - 1)
        if partition.next_partition_is_active:
            params.comm.Send(right, dest = rank + 1)

        # Receive particles from neighbors
        neighbor_particles = []
        if partition.previous_partition_is_active:
            params.comm.Recv(neighbor_particles, source = mpi.ANY_SOURCE)
        self.neighbor_particles.add(particle for particle in neighbor_particles)

        neighbor_particles = []
        if partition.next_partition_is_active:
            params.comm.Recv(neighbor_particles, source = mpi.ANY_SOURCE)
        self.neighbor_particles.add(particle for particle in neighbor_particles)

    def interact_particles(self):
        for particle in self.particles:
            particle.populate_neighbors(self.particles + self.neighbor_particles)
        for particle in self.particles:
            particle.update_velocity()
        for particle in self.particles:
            particle.update_position(dt)

    def exchange_particles(self):
        """Send particles that should now belong to neighboring partitions to
        neighbors, and receive any particles that now belong to this partition

        The sending partition updates the Particle's internal thread number
        before sending the Particle to the other partition
        """
        right, left = set(), set()
        for particle in particles:
            location = self.particle_is_not_in_range(particle)
            if location is -1:
                left.append(particle)
                particle.thread_num -= 1
            elif location is 1:
                right.append(particle)
                particle.thread_num += 1
        self.remove_particles(left)
        self.remove_particles(right)

        # Send neighbors their new particles
        if partition.previous_partition_is_active:
            params.comm.Send(left , dest = params.rank - 1)
        if partition.next_partition_is_active:
            params.comm.Send(right, dest = params.rank + 1)

        # Receive particles from neighbors
        new_particles = []
        if partition.previous_partition_is_active:
            params.comm.Recv(new_particles, source = mpi.ANY_SOURCE)
        partition.add_particles(new_particles)

        new_particles = []
        if partition.next_partition_is_active:
            params.comm.Recv(new_particles, source = mpi.ANY_SOURCE)
        partition.add_particles(new_particles)

    def update_master(self):
        """Update the master node with new particles"""
        params.comm.Send(self.particles)

