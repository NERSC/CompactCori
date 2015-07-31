#!/usr/bin/python

import util
import params

class Partition:
    """Partition class, where each Partition corresponds to the area of the
    simulation that a thread owns.

    Invariant: If Partition i is active (that is, if there are i threads working
    on the simulation), then for all partitions j < i, j is active as well

    When changing the ownership of a particle, the sending partition always changes
    the owner of each particle.  The reciving partition validates that the change
    was made correctly.
    """
    def __init__(self, thread_num):
        util.validate_int(thread_num)

        self.thread_num = thread_num
        self.particles = set()
        self.neighbor_particles = set()
        self.delta_x = params.simulation_width//params.num_threads
        self.start_x = self.delta_x*self.thread_num
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + self.delta_x

        params.num_active_workers += 1
        params.new_num_active_workers += 1

    def update_end_x(self):
        """This method is used to pick volume that does not evenly divide into
        the number of active workers when the number of workers changes
        """
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + self.delta_x

    def add_particles(self, particle_set):
        """ TODO: Is this method ever called?"""
        util.validate_particle_set(particle_set)
        for particle in particle_set:
            if particle.thread_num != self.thread_num:
                util.error("Thread numbers don't match: particle is " +
                        str(particle.thread_num) + " and self is: " +
                        str(self.thread_num))
        self.particles.union(particle_set)

    def add_particle(self, particle):
        if particle.thread_num != self.thread_num:
            util.error("Thread numbers don't match: particle is " +
                    str(particle.thread_num) + " and self is: " +
                    str(self.thread_num))
        self.particles.add(particle)

    def remove_particles(self, particle_set):
        util.validate_particle_set(particle_set)
        self.particles.difference_update(particle_set)

    def set_particles(self, particle_set):
        util.validate_particle_set(particle_set)
        for particle in particle_set:
            if particle.thread_num != self.thread_num:
                util.error("Thread numbers don't match: particle is " +
                        str(particle.thread_num) + " and self is: " +
                        str(self.thread_num))
        self.particles = particle_set

    def particle_is_not_in_range(self, particle):
        """Assumes that the particle will never be travelling fast
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
        return self.thread_num > 1 and self.thread_num - 1 <= params.num_active_workers

    def next_partition_is_active(self):
        return self.thread_num + 1 <= params.num_active_workers

    def send_and_receive_neighboring_particles(self):
        """Send particles that may interact with another partitions particles,
        and receive other partitions' particles that may interact with this
        partition's particles
        """
        right, left = self.handoff_neighboring_particles()

        # Update neighbors with my particles
        if self.previous_partition_is_active():
            params.comm.send(left, dest = self.thread_num - 1, tag = 1)
        if self.next_partition_is_active():
            params.comm.send(right, dest = self.thread_num + 1, tag = 1)

        # Receive particles from neighbors
        self.neighbor_particles = set()
        if self.previous_partition_is_active():
            neighbor_particles = params.comm.recv(source = params.mpi.ANY_SOURCE, tag = 1)
            self.neighbor_particles.union(neighbor_particles)

        if self.next_partition_is_active():
            neighbor_particles = params.comm.recv(source = params.mpi.ANY_SOURCE, tag = 1)
            self.neighbor_particles.union(particle for particle in neighbor_particles)

    def interact_particles(self):
        for particle in self.particles:
            particle.populate_neighbors(self.particles | self.neighbor_particles)
        for particle in self.particles:
            particle.update_velocity()
        for particle in self.particles:
            particle.update_position(params.dt)

    def exchange_particles(self):
        """Send particles that should now belong to neighboring partitions to
        neighbors, and receive any particles that now belong to this partition

        The sending partition updates the Particle's internal thread number
        before sending the Particle to the other partition
        """
        right, left = set(), set()
        for particle in self.particles:
            if particle.thread_num != params.rank:
                debug("Rank is " + str(params.rank) + "but particle has thread number " + str(particle.thread_num))
            location = self.particle_is_not_in_range(particle)
            if location is -1:
                left.add(particle)
                particle.thread_num -= 1
            elif location is 1:
                right.add(particle)
                particle.thread_num += 1
        self.remove_particles(left)
        self.remove_particles(right)

        # Send neighbors their new particles
        if self.previous_partition_is_active():
            params.comm.send(left, dest = params.rank - 1, tag = 10)
        if self.next_partition_is_active():
            params.comm.send(right, dest = params.rank + 1, tag = 10)

        # Receive particles from neighbors
        if self.previous_partition_is_active():
            new_particles = params.comm.recv(source = params.mpi.ANY_SOURCE, tag = 10)
            self.add_particles(new_particles)

        if self.next_partition_is_active():
            new_particles = params.comm.recv(source = params.mpi.ANY_SOURCE, tag = 10)
            self.add_particles(new_particles)

    def update_master(self):
        """Update the master node with new particles"""
        params.comm.send(self.particles, tag = 00)

    def receive_new_particles(self):
        """Receive new particle set after changing the number of threads"""
        new_particles = params.comm.recv(source = 1, tag = 11)
        self.set_particles(new_particles)
        self.update_end_x()
