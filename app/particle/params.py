#!/usr/bin/python
"""Global parameters"""

num_particles = None
simulation_height = None
simulation_width = None
simulation_depth = None
dt = None
num_active_workers = None
partitions = {}
max_radius = None

comm = None
rank = None
num_threads = None

def determine_particle_thread_num(x_position, num_active_workers = num_active_workers):
    return math.ceil((x_position/simulation_width)*num_active_workers)

