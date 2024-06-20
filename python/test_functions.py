import unittest
from python.Grid import Grid
import numpy as np


class TestMulticell(unittest.TestCase):

    poss = [[1, 2], [1, 2, 3], [1, 2]]

    poss = [list([2, 7, 11, 14]), list([4, 7]), 6, list([4, 11]), 3, 5,
            list([2, 4, 12, 14]), list([4, 14]), 16, list([7, 8, 10, 15]), 9,
            list([4, 8, 10, 15]), list([8, 11, 12]), 13, 1, list([4, 11])]
