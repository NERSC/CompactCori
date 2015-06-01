#!/usr/bin/python
"""
Unit test file for particle_simulation.py
"""
import unittest
from particle_simulation import Particle

class TestParticleMethods(unittest.TestCase):
    def test_euclidean_distance(self):
        a = Particle(1, 10, 10)
        b = Particle(1, 10, 20)
        self.assertEqual(a.euclidean_distance_to(b), (10, 0, 10))

        a = Particle(1, 0, 0)
        b = Particle(1, 0, 0)
        self.assertEqual(a.euclidean_distance_to(b), (0, 0, 0))

        a = Particle(1, -10, 20)
        b = Particle(1, 10, 20)
        self.assertEqual(a.euclidean_distance_to(b), (20, 20, 0))

        a = Particle(1, -18, 24)
        b = Particle(1, 7, 32)
        self.assertEqual(a.euclidean_distance_to(b), (26.248809496813376, 25, 8))

        a = Particle(1, -100, 0)
        b = Particle(1, -0.01, 0)
        self.assertEqual(a.euclidean_distance_to(b), (99.99, 99.99, 0))

    def test_populate_neighbors(self):
        a = Particle(1, -100, 0)
        b = Particle(1, 100, 1)
        c = Particle(1,250,100)
        Particle.static_particles = [a,b,c]
        self.assertEqual(Particle.static_particles, [a,b,c])

        b.populate_neighbors()
        self.assertEqual(b.neighbors, [])

        b = Particle(1, -0.01, 0)
        Particle.static_particles = [a,b,c]
        self.assertEqual(Particle.static_particles, [a,b,c])

        a.populate_neighbors()
        b.populate_neighbors()
        print("Neighbors: " + str(b.neighbors))
        dist = a.euclidean_distance_to(b)
        self.assertEqual(len(b.neighbors), 1)
        self.assertEqual(b.neighbors[0], (a, dist[1], dist[2]))

if __name__ == '__main__':
    unittest.main()
