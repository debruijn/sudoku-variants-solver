import numpy as np


class Grid:

    def __init__(self, given_values, boxes=None):
        self.size = given_values.shape[0]
        if boxes is not None:
            self.boxes = boxes
            self.default_boxes = False
        else:
            self.boxes = self.gen_default_boxes()
            self.default_boxes = True
        self.given_values = given_values
        self.known_values = given_values
        self.possible_values = np.empty([self.size, self.size], dtype=object)
        for i in range(self.size):
            for j in range(self.size):
                self.possible_values[i, j] = [x for x in range(1, self.size+1)]
        self.gen_possible_values()

    def gen_default_boxes(self):
        if self.size == 4:
            boxes = np.row_stack([np.repeat([np.repeat([1, 2], 2)], 2, axis=0),
                                  np.repeat([np.repeat([3, 4], 2)], 2, axis=0)])
        elif self.size == 6:
            boxes = np.row_stack([np.repeat([np.repeat([1, 2], 3)], 2, axis=0),
                                  np.repeat([np.repeat([3, 4], 3)], 2, axis=0),
                                  np.repeat([np.repeat([5, 6], 3)], 2, axis=0)])
        elif self.size == 9:
            boxes = np.row_stack([np.repeat([np.repeat([1, 2, 3], 3)], 3, axis=0),
                                  np.repeat([np.repeat([4, 5, 6], 3)], 3, axis=0),
                                  np.repeat([np.repeat([7, 8, 9], 3)], 3, axis=0)])
        elif self.size == 12:
            boxes = np.row_stack([np.repeat([np.repeat([1, 2, 3], 4)], 3, axis=0),
                                  np.repeat([np.repeat([4, 5, 6], 4)], 3, axis=0),
                                  np.repeat([np.repeat([7, 8, 9], 4)], 3, axis=0),
                                  np.repeat([np.repeat([10, 11, 12], 4)], 3, axis=0)])
        elif self.size == 16:
            boxes = np.row_stack([np.repeat([np.repeat([1, 2, 3, 4], 4)], 4, axis=0),
                                  np.repeat([np.repeat([5, 6, 7, 8], 4)], 4, axis=0),
                                  np.repeat([np.repeat([9, 10, 11, 12], 4)], 4, axis=0),
                                  np.repeat([np.repeat([13, 14, 15, 16], 4)], 4, axis=0)])
        elif self.size == 25:
            boxes = np.row_stack([np.repeat([np.repeat([1, 2, 3, 4, 5], 5)], 5, axis=0),
                                  np.repeat([np.repeat([6, 7, 8, 9, 10], 5)], 5, axis=0),
                                  np.repeat([np.repeat([11, 12, 13, 14, 15], 5)], 5, axis=0),
                                  np.repeat([np.repeat([16, 17, 18, 19, 20], 5)], 5, axis=0),
                                  np.repeat([np.repeat([21, 22, 23, 24, 25], 5)], 5, axis=0)])
        else:
            boxes = None

        return boxes

    def gen_possible_values_cell(self, i, j, full_check=False):
        if self.known_values[i, j] > 0:
            self.possible_values[i, j] = self.known_values[i, j]
        else:
            if full_check:
                self.possible_values[i, j] = [x for x in range(1, self.size + 1)]
            possibles = self.possible_values[i, j].copy()
            for k in possibles:
                if any([(k in self.known_values[:, j]),
                        (k in self.known_values[i, :]),
                        (k in self.known_values[self.boxes == self.boxes[i, j]])]):
                    self.possible_values[i, j].remove(k)
        return self.possible_values[i, j]

    def gen_possible_values(self, full_check=False):
        for i in range(self.size):
            for j in range(self.size):
                self.gen_possible_values_cell(i, j, full_check)

        return self.possible_values

    def get_possible_values(self, i, j, update_cell=False):
        if update_cell:
            self.gen_possible_values_cell(i, j, full_check=False)
        return self.possible_values[i, j]

    def check_potential_values(self):
        at_least_one_update = False
        for i in range(self.size):
            for j in range(self.size):
                if isinstance(self.possible_values[i, j], list):
                    if len(self.possible_values[i, j]) == 1:
                        at_least_one_update = True
                        self.known_values[i, j] = self.possible_values[i, j][0]
                        self.possible_values[i, j] = self.possible_values[i, j][0]

        return at_least_one_update
