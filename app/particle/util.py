#!/usr/bin/python
"""Utility functions"""
import params
import math
import traceback
from Particle import Particle

def info(string):
    """Print a message in blue to STDOUT"""
    CSI="\x1B["
    print(CSI + "31;36m" + "[INFO]     " + string + CSI + "31;0m")

def debug(string):
    """Print a message in yellow to STDOUT"""
    CSI="\x1B["
    print(CSI + "31;93m" + "[DEBUG]    " + string + CSI + "31;0m")

def error(string):
    """Print a message in red to STDOUT and print a stack trace"""
    CSI="\x1B["
    print(CSI + "31;31m" + "[ERROR]    " + string + CSI + "31;0m")
    print("Stack:")
    traceback.print_stack()
    exit(1)

def validate_int(*args):
    for arg in args:
        if type(arg) is not int:
            error(ArgumentError, "incorrect type argument: " + type(arg) +
                "was passed instead of a int")

def validate_list(*args):
    for arg in args:
        if type(arg) is not list:
            error(ArgumentError, "incorrect type argument: " + type(arg) +
                "was passed instead of a int")

def validate_particle_set(*args):
    for arg in args:
        if type(arg) is not set:
            error(ArgumentError, "incorrect type argument: " + type(arg) +
                "was passed instead of a set")
        for obj in arg:
            if type(obj) is not Particle:
                error(ArgumentError, "Non-particle type in set; received a " +
                        type(obj) + " instead of a Particle")

def determine_particle_thread_num(x_position):
    return math.ceil((x_position/params.simulation_width)*params.num_active_workers)

