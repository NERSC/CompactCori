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
import sys

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
        """Delta calculation assumes that there will be num_threads - 1
        partitions since num_active_workers is incremented within the
        constructor
        """
        util.validate_int(thread_num)

        self.thread_num = thread_num
        self.particles = set()
        self.neighbor_particles = set()
        self.delta_x = params.simulation_width//(params.num_threads - 1)
        self.start_x = self.delta_x*(self.thread_num-1)
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + self.delta_x

        params.num_active_workers += 1
        params.new_num_active_workers += 1

    def update_start_end(self):
        """This method is used to pick volume that does not evenly divide into
        the number of active workers when the number of workers changes

        Note that the delta is calculated based on the number of active workers
        and not the number of threads, since the number of threads no longer
        necessarily correlates to the number of active workers
        """
        self.delta_x = params.simulation_width//(params.num_active_workers - 1)
        self.start_x = self.delta_x*(self.thread_num-1)
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + self.delta_x

    def add_particles(self, particle_set):
        """Add multiple Particles to the set of Particles that this Partition is
        responsible for
        """
        util.validate_particle_set(particle_set)
        for particle in particle_set:
            if particle.thread_num != self.thread_num:
                util.error("Thread numbers don't match: particle is " +
                        str(particle.thread_num) + " and self is: " +
                        str(self.thread_num))
        self.particles = self.particles.union(particle_set)

    def add_particle(self, particle):
        """Add a single Particle to the set of Particles that this Partition is
        responsible for
        """
        if particle.thread_num != self.thread_num:
            util.error("Thread numbers don't match: particle is " +
                    str(particle.thread_num) + " and self is: " +
                    str(self.thread_num))
        self.particles.add(particle)

    def remove_particles(self, particle_set):
        """Remove a set of particles from this Partition"""
        util.validate_particle_set(particle_set)
        self.particles.difference_update(particle_set)

    def set_particles(self, particle_set):
        """Overwrite the set of Particles that tis Partition is responsible for.
        This is used when changing the number of Partitions
        """
        util.validate_particle_set(particle_set)
        for particle in particle_set:
            if particle.thread_num != self.thread_num:
                util.error("Thread numbers don't match: particle is " +
                        str(particle.thread_num) + " and self is: " +
                        str(self.thread_num))
        self.particles = particle_set

    def particle_is_not_in_range(self, particle):
        """Helps determine whether or not a Particle belongs to this Partition
        or another partition.  This method assumes that the particle will never
        be travelling fast enough to jump more than one partition at a time.

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
        """This method returns all particles that touch the border between
        neighboring partitions
        """
        right = set()
        left = set()
        for particle in self.particles:
            if particle.position[0] + particle.radius + params.max_radius > self.end_x:
                right.add(particle)
            elif particle.position[0] - particle.radius - params.max_radius < self.start_x:
                left.add(particle)
        return (right, left)

    def neighboring_sendrecv(self, sendobj, source_destination, tag):
        """This helper method performs a sendrecv for
        send_and_receive_neighboring_particles
        """
        neighbor_particles = params.comm.sendrecv(sendobj = sendobj,
                dest = source_destination, sendtag = tag,
                source = source_destination, recvtag = tag)
        self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

    def send_and_receive_neighboring_particles(self):
        """Call handoff_neighboring_particles to get all particles that touch
        the border between this partition and its one (or two) neighbors.  Then
        send the neighbor the particle set and add the set that it sends to this
        Partition to self.neighbor_particles by calling neighboring_sendrecv

        There are two steps:
        1. Rank 1 and 2 exchange while
           Rank 3 and 4 exchange while
           ...
        2. Rank 2 and 3 exchange while
           Rank 4 and 5 exchange while
           ...
        """
        right, left = self.handoff_neighboring_particles()
        self.neighbor_particles = set()

        if params.rank == 1:
            self.neighboring_sendrecv(right, self.thread_num + 1, 1)

        elif params.rank == params.num_active_workers and params.rank % 2 == 0:
            self.neighboring_sendrecv(left, self.thread_num - 1, 1)

        elif params.rank == params.num_active_workers and params.rank % 2 == 1:
            self.neighboring_sendrecv(left, self.thread_num - 1, 2)

        elif params.rank % 2 == 0:
            self.neighboring_sendrecv(left, self.thread_num - 1, 1)
            self.neighboring_sendrecv(right, self.thread_num + 1, 2)

        else:
            self.neighboring_sendrecv(right, self.thread_num + 1, 1)
            self.neighboring_sendrecv(left, self.thread_num - 1, 2)

    def interact_particles(self):
        """Do computation and interact particles within this Partition.
        Includes interactions between particles that are bordering this
        Partition.  Update the velocity and the position of each particle
        """
        for particle in self.particles:
            particle.update_velocity(self.particles | self.neighbor_particles)
#        for particle in self.particles:
#            particle.update_velocity()
        for particle in self.particles:
            particle.update_position(params.dt)

    def exchange_sendrecv(self, increment, sendobj, source_destination, tag):
        """This helper method removes the particles from this Partition,
        decrements or incrments each particle's thread number, and then performs
        a sendrecv for exchange_particles
        """
        self.remove_particles(sendobj)
        if increment:
            for particle in sendobj:
                particle.thread_num += 1
        else:
            for particle in sendobj:
                particle.thread_num -= 1
        new_particles = params.comm.sendrecv(sendobj = sendobj,
                dest = source_destination, sendtag = tag,
                source = source_destination, recvtag = tag)
        self.add_particles(new_particles)

    def exchange_particles(self):
        """Send particles that should now belong to neighboring partitions to
        neighbors, and receive any particles that now belong to this partition

        Call particle_is_not_in_range for each particle to determine which
        particles should now belong to a different Partition.

        Then, remove the particles from this Partition's list of particles,
        decrement or increment each particle's thread number, and send the
        neighbor the particle set to the respective neighbor using
        exchange_sendrecv.  Also add the set that it sends to this Partition to
        self.particles

        There are two steps in the exchange:
        1. Rank 1 and 2 exchange while
           Rank 3 and 4 exchange while
           ...
        2. Rank 2 and 3 exchange while
           Rank 4 and 5 exchange while
           ...
        """
        sys.stdout.flush()
        right, left = set(), set()
        for particle in self.particles:
            if particle.thread_num != params.rank:
                util.debug("Rank is " + str(params.rank) + " but particle has thread number " + str(particle.thread_num))
            switch = self.particle_is_not_in_range(particle)
            if switch is -1:
                left.add(particle)
            elif switch is 1:
                right.add(particle)

        # Send neighbors their new particles
        if params.rank == 1:
            self.exchange_sendrecv(True, right, self.thread_num + 1, 1)

        elif params.rank == params.num_active_workers and params.rank % 2 == 0:
            self.exchange_sendrecv(False, left, self.thread_num - 1, 1)

        elif params.rank == params.num_active_workers and params.rank % 2 == 1:
            self.exchange_sendrecv(False, left, self.thread_num - 1, 2)

        elif params.rank % 2 == 0:
            self.exchange_sendrecv(False, left, self.thread_num - 1, 1)
            self.exchange_sendrecv(True, right, self.thread_num + 1, 2)

        else:
            self.exchange_sendrecv(True, right, self.thread_num + 1, 1)
            self.exchange_sendrecv(False, left, self.thread_num - 1, 2)

    def update_master(self):
        """Update the master node with new particles"""
#        if len(self.particles) is not 0:
#            util.debug("Rank " + str(params.rank) + " is sending back " + str(len(self.particles)) + " particles")
        params.comm.send(self.particles, tag = 0)

    def receive_new_particles(self):
        """Receive new particle set after changing the number of threads"""
        new_particles = params.comm.recv(source = 1, tag = 11)
        self.set_particles(new_particles)
        self.update_start_x()
        self.update_start_end()

    def __repr__(self):
        """Represent a Partition by the number of particles that the Partition
        is responsible for
        """
        return str(len(self.particles))
