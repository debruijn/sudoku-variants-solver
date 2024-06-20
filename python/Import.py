from python.Grid import Grid
import numpy as np


def import_text(string):

    grid = Grid(np.reshape([np.int(x) for x in string.replace('.', '0')], (9, 9)))
    return grid


def import_csv():

    pass
