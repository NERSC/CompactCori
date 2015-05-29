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

if __name__ == '__main__':
    unittest.main()
