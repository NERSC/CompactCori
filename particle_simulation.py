#!/usr/bin/python
"""
A parallelized MD simulation in Python written for version 1 of the Compact Cory
project at NERSC.

This runs in O(n^2) time since all particles are compared to one another when
locating in-range neighbors.
"""
import argparse
import random
import math
import copy
import tkinter as tk

class Application(tk.Frame):
    def say_hi(self):
        print("hi there, everyone!")

    def createWidgets(self):
        self.QUIT = tk.Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

#root = tk.Tk()
#app = Application(master=root)
#canvas = tk.Canvas(root, width = 300, height = 300)
#canvas.pack()
#app.master.title("Particle Simulation")
#app.mainloop()
#root.destroy()
canvas = None

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--numparticles", type=int,
        help = "number of particles in simulation")
parser.add_argument("-r", "--radius", type=int,
        help = "radius of particle interaction")
parser.add_argument("-f", "--force", type=int,
        help = "force between particles")
parser.add_argument("--height", type=int,
        help = "height of simulation window")
parser.add_argument("--width", type=int,
        help = "width of simulation window")
parser.add_argument("-d", "--dt", type=float,
        help = "multiplier time constant")
args = parser.parse_args()

num_particles = args.numparticles if args.numparticles else 20
interaction_radius = args.radius if args.radius else 100
force_amount = args.force if args.force else 50
simulation_height = args.height if args.height else 1000
simulation_width = args.width if args.width else 1000
force_constant = args.force if args.force else 1
dt = args.dt if args.dt else 0.0005

particles = []

class Particle:
    static_particles = particles
    def __init__(self, mass = 1, x_position = None, y_position = None, x_velocity = 0, y_velocity = 0):
        self.x_position = x_position if (x_position != None) else random.randint(0, simulation_width - 1)
        self.y_position = y_position if (y_position != None) else random.randint(0, simulation_height - 1)
        self.x_velocity = x_velocity if (x_velocity != None) else random.randint(-1*simulation_height//10, simulation_height//10)
        self.y_velocity = y_velocity if (y_velocity != None) else random.randint(-1*simulation_height//10, simulation_height//10)
        self.mass = mass
        self.neighbors = None
        self.x_accel = 0
        self.y_accel = 0

    def euclidean_distance_to(self, particle):
        x = abs(self.x_position - particle.x_position)
        y = abs(self.y_position - particle.y_position)
        return (math.sqrt((x**2) + (y**2)), x, y)

    def populate_neighbors(self):
        self.neighbors = []
        for particle in Particle.static_particles:
            euclidean_distance, x_distance, y_distance = self.euclidean_distance_to(particle)
            if euclidean_distance < interaction_radius and particle is not self:
                self.neighbors.append((particle, x_distance, y_distance))

    def calculate_force(self, particle, x_distance, y_distance):
        x = force_constant * (self.mass * particle.mass)/(x_distance**2) if x_distance else 0
        y = force_constant * (self.mass * particle.mass)/(y_distance**2) if y_distance else 0
        return x,y

    def calculate_net_force(self):
        self.x_accel = 0
        self.y_accel = 0
        for neighbor, x_distance, y_distance in self.neighbors:
            x, y = self.calculate_force(neighbor, x_distance, y_distance)
            self.x_accel += x * x_distance
            self.y_accel += y * y_distance

    def move_particle(self):
        """
        Naively assumes velocity is less than the size of the simulation window
        """
        self.x_velocity += self.x_accel * dt
        self.y_velocity += self.y_accel * dt

        self.x_position += self.x_velocity * dt
        self.y_position += self.y_velocity * dt

        while self.x_position < 0 or self.x_position > simulation_width:
            self.x_position = self.x_position*-1 if self.x_position < 0 else 2*simulation_width - self.x_position
            self.x_velocity *= -1

        while self.y_position < 0 or self.y_position > simulation_height:
            self.y_position = self.y_position*-1 if self.y_position < 0 else 2*simulation_height - self.y_position
            self.y_velocity *= -1

        self.x_position = int(self.x_position)
        self.y_position = int(self.y_position)

    def __repr__(self):
        if self.neighbors:
            return "Currently located at: (" + str(self.x_position) + "," + str(self.y_position) + ") with " + str(len(self.neighbors)) + " neighbors\n"
        else:
            return "Currently located at: (" + str(self.x_position) + "," + str(self.y_position) + ") with " + str(self.neighbors) + " neighbors\n"

# Create Particles
for _ in range(num_particles):
    particles.append(Particle())

def text_simulation():
    """
    Print out an ASCII-based representation of the simulation to STDOUT
    """
    # Populate nested list
    arr = [[" "] * simulation_height for _ in range(simulation_width)]
    for particle in particles:
        arr[particle.x_position][particle.y_position] = "o"

    # Convert list to buffer to print to STDOUT
    buf = " "
    for i in range(simulation_width):
        buf += str(i % 10)
    buf += "\n " + "-" * simulation_width + "\n"
    for j in range(simulation_height):
        buf += "|"
        for i in range(simulation_width):
            buf += arr[i][j]
        buf += "|" +  str(j) + "\n"
    buf += " " + "-" * simulation_width
    print(buf)

# One timestep
def timestep():
    for particle in particles:
        particle.populate_neighbors()
    for particle in particles:
        particle.calculate_net_force()
    for particle in particles:
        particle.move_particle()

# Run simulation
#while True:
for i in range(300):
    timestep()
    text_simulation()

