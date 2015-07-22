#!/usr/bin/python

class Partition:
    """Partition class, where each Partition corresponds to the area of the
    simulation that a thread owns.

    Invariant: If Partition i is active (that is, if there are i threads working
    on the simulation), then for all partitions j < i, j is active as well

    TODO: Ensure that the last partition picks up any coordinates that would
    otherwise be ignored due to floor
    """
    partitions = {}
    def __init__(self, thread_num):
        validate_int(thread_num)

        self.thread_num = thread_num
        self.particles = set()
        self.delta_x = simulation_width//num_threads
        self.start_x = self.delta_x*self.thread_num
        self.end_x = self.start_x + delta_x
        self.active = True
        partitions[thread_num] = self

    def update_neighbor_thread_set(self):
        #TODO: FIX NUM_THREADS
        # If partition 0 and partition 1 is active
        if self.thread_num is 0 and partitions[1].active:
            self.neighbor_threads = set(1)
        # If partition 0 and partition 1 is inactive
        elif self.thread_num is 0 and not partitions[1].active:
            self.neighbor_threads = set()
        # If last partition
        elif self.thread_num is num_threads - 1:
            self.neighbor_threads = set(num_threads - 2)
        # If any other partition and the next partition is inactive
        elif not partitions[thread_num + 1].active:
            self.neighbor_threads = set(thread_num - 1)
        # If any other partition and the next partition is active
        else:
            self.neighbor_threads = set(thread_num - 1, thread_num + 1)

    def add_particles(self, particle_set):
        validate_particle_set(particle_set)
        self.particles.union(particle_set)

    def remove_particles(self, particle_set):
        validate_particle_set(particle_set)
        self.particles.difference_update(particle_set)

    def set_particles(self, particle_set):
        validate_particle_set(particle_set)
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

    def handoff(self):
        right = set()
        left = set()
        for particle in self.particles:
            if particle.position[0] + particle.radius + particle.max_radius > self.end_x:
                right.add(particle)
            elif particle.position[0] - particle.radius - particle.max_radius < self.start_x:
                left.add(particle)
        return (right, left)

    def _able(self, active):
        if self.thread_num is 0:
            partitions[thread_num + 1].update_neighbor_thread_set()
        elif self.thread_num is num_threads - 1:
            partitions[thread_num - 1].update_neighbor_thread_set()
        else:
            partitions[thread_num + 1].update_neighbor_thread_set()
            partitions[thread_num - 1].update_neighbor_thread_set()
        self.active = active

    def enable(self):
        self._able(True)

    def disable(self):
        self._able(False)
