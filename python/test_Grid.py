import unittest
from python.Grid import Grid
import numpy as np


class TestGrid(unittest.TestCase):

    def test_possible_values_cell(self):

        g = Grid(np.array([[1, 2], [0, 0]]), boxes=np.array([[1, 1], [2, 2]]))
        self.assertEqual(g.gen_possible_values_cell(1, 0), [2])

        g.possible_values[1, 0] = []
        self.assertEqual(g.gen_possible_values_cell(1, 0), [])

        self.assertEqual(g.gen_possible_values_cell(1, 0, full_check=True), [2])

    def test_possible_values_overall(self):

        g = Grid(np.array([[1, 2], [0, 0]]), boxes=np.array([[1, 1], [2, 2]]))
        self.assertEqual(g.gen_possible_values()[1, 0], [2])

        g.possible_values[1, 0] = []
        self.assertEqual(g.gen_possible_values()[1, 0], [])

        self.assertEqual(g.gen_possible_values(full_check=True)[1, 0], [2])

    def test_get_possible_values_cell(self):

        g = Grid(np.array([[1, 2], [0, 0]]), boxes=np.array([[1, 1], [2, 2]]))
        self.assertEqual(g.get_possible_values(1, 0), [2])

        g.known_values[1, 1] = 2
        self.assertEqual(g.get_possible_values(1, 0), [2])

        self.assertEqual(g.get_possible_values(1, 0, update_cell=True), [])

    def test_convert_potentials_to_known_false(self):

        g = Grid(np.array([[0, 0], [0, 0]]), boxes=np.array([[1, 1], [2, 2]]))
        self.assertFalse(g.check_potential_values())

    def test_convert_potentials_to_known_true(self):
        g = Grid(np.array([[1, 2], [0, 0]]), boxes=np.array([[1, 1], [2, 2]]))
        self.assertTrue(g.check_potential_values())
