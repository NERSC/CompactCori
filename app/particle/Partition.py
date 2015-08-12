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
        util.validate_int(thread_num)

        self.thread_num = thread_num
        self.particles = set()
        self.neighbor_particles = set()
        self.delta_x = params.simulation_width//(params.num_threads - 1)
        self.start_x = self.delta_x*(self.thread_num-1)
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + self.delta_x

        params.num_active_workers += 1
        params.new_num_active_workers += 1

    def update_end_x(self):
        """This method is used to pick volume that does not evenly divide into
        the number of active workers when the number of workers changes
        """
        self.end_x = params.simulation_width if self.thread_num is params.num_active_workers else self.start_x + self.delta_x

    def add_particles(self, particle_set):
        util.validate_particle_set(particle_set)
        for particle in particle_set:
            if particle.thread_num != self.thread_num:
                util.error("Thread numbers don't match: particle is " +
                        str(particle.thread_num) + " and self is: " +
                        str(self.thread_num))
        self.particles = self.particles.union(particle_set)

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

    def neighboring_sendrecv(self, sendobj, source_destination, tag):
        neighbor_particles = params.comm.sendrecv(sendobj = sendobj,
                dest = source_destination, sendtag = tag,
                source = source_destination, recvtag = tag)
#        util.debug("Updating by adding " + str(neighbor_particles))
        self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

    def send_and_receive_neighboring_particles(self):
        """Send particles that may interact with another partitions particles,
        and receive other partitions' particles that may interact with this
        partition's particles
        """
        # TODO: DRY THIS OUT
        right, left = self.handoff_neighboring_particles()

        if params.rank == 1:
            self.neighboring_sendrecv(right, self.thread_num + 1, 1)
#            neighbor_particles = params.comm.sendrecv(sendobj = right, dest = self.thread_num + 1, sendtag = 1, source = self.thread_num + 1, recvtag = 1)
#            self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

        elif params.rank == params.num_active_workers and params.rank % 2 == 0:
            self.neighboring_sendrecv(left, self.thread_num - 1, 1)
#            neighbor_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 1, source = self.thread_num - 1, recvtag = 1)
#            self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

        elif params.rank == params.num_active_workers and params.rank % 2 == 1:
            self.neighboring_sendrecv(left, self.thread_num - 1, 2)
#            neighbor_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 2, source = self.thread_num - 1, recvtag = 2)
#            self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

        elif params.rank % 2 == 0:
            self.neighboring_sendrecv(left, self.thread_num - 1, 1)
#            neighbor_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 1, source = self.thread_num - 1, recvtag = 1)
#            self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

            self.neighboring_sendrecv(right, self.thread_num + 1, 2)
#            neighbor_particles = params.comm.sendrecv(sendobj = right, dest = self.thread_num + 1, sendtag = 2, source = self.thread_num + 1, recvtag = 2)
#            self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

        else:
            self.neighboring_sendrecv(right, self.thread_num + 1, 1)
#            neighbor_particles = params.comm.sendrecv(sendobj = right, dest = self.thread_num + 1, sendtag = 1, source = self.thread_num + 1, recvtag = 1)
#            self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

            self.neighboring_sendrecv(left, self.thread_num - 1, 2)
#            neighbor_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 2, source = self.thread_num - 1, recvtag = 2)
#            self.neighbor_particles = self.neighbor_particles.union(neighbor_particles)

    def interact_particles(self):
        for particle in self.particles:
            particle.populate_neighbors(self.particles | self.neighbor_particles)
        for particle in self.particles:
            particle.update_velocity()
        for particle in self.particles:
            particle.update_position(params.dt)

    def exchange_sendrecv(self, increment, sendobj, source_destination, tag):
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
        for particle in new_particles:
            util.debug("Adding new particles " + str(particle))
        self.add_particles(new_particles)

    def exchange_particles(self):
        """Send particles that should now belong to neighboring partitions to
        neighbors, and receive any particles that now belong to this partition

        The sending partition updates the Particle's internal thread number
        before sending the Particle to the other partition
        """
        sys.stdout.flush()
        right, left = set(), set()
        for particle in self.particles:
            if particle.thread_num != params.rank:
                util.debug("Rank is " + str(params.rank) + " but particle has thread number " + str(particle.thread_num))
            location = self.particle_is_not_in_range(particle)
            if location is -1:
                left.add(particle)
            elif location is 1:
                right.add(particle)

        # Send neighbors their new particles
        # TODO: DRY THIS OUT
        if params.rank == 1:
            self.exchange_sendrecv(True, right, self.thread_num + 1, 1)
#            self.remove_particles(right)
#            for particle in right:
#                particle.thread_num += 1
#            new_particles = params.comm.sendrecv(sendobj = right, dest = self.thread_num + 1, sendtag = 1, source = self.thread_num + 1, recvtag = 1)
#            self.add_particles(new_particles)

        elif params.rank == params.num_active_workers and params.rank % 2 == 0:
            self.exchange_sendrecv(False, left, self.thread_num - 1, 1)
#            self.remove_particles(left)
#            for particle in left:
#                particle.thread_num -= 1
#            new_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 1, source = self.thread_num - 1, recvtag = 1)
#            self.add_particles(new_particles)

        elif params.rank == params.num_active_workers and params.rank % 2 == 1:
            self.exchange_sendrecv(False, left, self.thread_num - 1, 2)
#            self.remove_particles(left)
#            for particle in left:
#                particle.thread_num -= 1
#            new_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 2, source = self.thread_num - 1, recvtag = 2)
#            self.add_particles(new_particles)

        elif params.rank % 2 == 0:
            self.exchange_sendrecv(False, left, self.thread_num - 1, 1)
#            self.remove_particles(left)
#            for particle in left:
#                particle.thread_num -= 1
#            new_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 1, source = self.thread_num - 1, recvtag = 1)
#            self.add_particles(new_particles)

            self.exchange_sendrecv(True, right, self.thread_num + 1, 2)
#            self.remove_particles(right)
#            for particle in right:
#                particle.thread_num += 1
#            new_particles = params.comm.sendrecv(sendobj = right, dest = self.thread_num + 1, sendtag = 2, source = self.thread_num + 1, recvtag = 2)
#            self.add_particles(new_particles)

        else:
            self.exchange_sendrecv(True, right, self.thread_num + 1, 1)
#            self.remove_particles(right)
#            for particle in right:
#                particle.thread_num += 1
#            new_particles = params.comm.sendrecv(sendobj = right, dest = self.thread_num + 1, sendtag = 1, source = self.thread_num + 1, recvtag = 1)
#            self.add_particles(new_particles)

            self.exchange_sendrecv(False, left, self.thread_num - 1, 2)
#            self.remove_particles(left)
#            for particle in left:
#                particle.thread_num -= 1
#            new_particles = params.comm.sendrecv(sendobj = left, dest = self.thread_num - 1, sendtag = 2, source = self.thread_num - 1, recvtag = 2)
#            self.add_particles(new_particles)

    def update_master(self):
        """Update the master node with new particles"""
#        if len(self.particles) is not 0:
#            util.debug("Rank " + str(params.rank) + " is sending back " + str(len(self.particles)) + " particles")
        params.comm.send(self.particles, tag = 0)

    def receive_new_particles(self):
        """Receive new particle set after changing the number of threads"""
        new_particles = params.comm.recv(source = 1, tag = 11)
        self.set_particles(new_particles)
        self.update_end_x()

    def __repr__(self):
        return str(len(self.particles))
