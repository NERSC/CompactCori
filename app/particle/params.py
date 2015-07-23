#!/usr/bin/python
"""Global parameters"""

params.num_particles = None
params.radius = None
params.simulation_height = None
params.simulation_width = None
params.simulation_depth = None
params.dt = None
params.num_active_workers = None
params.partitions = None
params.max_radius = min(simulation_width, simulation_height, simulation_depth)/32

def determine_particle_thread_num(x_position):
    return math.ceil((x_position/simulation_width)*num_active_workers)

