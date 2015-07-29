#!/usr/bin/python
"""Utility functions"""

def debug(string):
    """Print a message in yellow to STDOUT"""
    CSI="\x1B["
    print(CSI + "31;93m" + "[DEBUG]    " + string + CSI + "31;0m")

def error(err, string):
    """Print a message in red to STDOUT and raise an exception"""
    CSI="\x1B["
    print(CSI + "31;31m" + "[ERROR]    " + string + CSI + "31;0m")
    raise err(CSI + "31;31m" + string + CSI + "31;0m")

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
