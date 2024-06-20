from abc import ABC, abstractmethod
import numpy as np


class Sudoku(ABC):

    def __init__(self, size=9, grid=None):
        if grid is not None:
            self.size = grid.size
        else:
            self.size = size
        self.grid = grid
        self.possible_locations = np.empty([self.size, self.size, self.size])
        self.possible_locations[:] = 1
        self.gen_potential_location()
        self.max_degree = 0
        self.box_size = np.int(np.ceil(np.sqrt(self.size)))

    @abstractmethod
    def check_solution(self, grid):
        pass

    @abstractmethod
    def check_intermediate(self, grid):
        pass

    @abstractmethod
    def step_solve(self):
        pass

    @abstractmethod
    def force_solve(self):
        pass

    @abstractmethod
    def solve(self):
        pass

    def check_potential_values(self):
        return self.grid.check_potential_values()

    def gen_possible_values(self, full_check=False):
        return self.grid.gen_possible_values(full_check=full_check)

    def gen_potential_location(self, full_check=False):

        if full_check:
            self.possible_locations[:] = 1

        for num in range(1, self.size+1):
            for i in range(self.size):
                for j in range(self.size):
                    possibles = self.grid.get_possible_values(i, j)
                    if isinstance(possibles, list):
                        if num not in possibles:
                            self.possible_locations[num-1, i, j] = 0
                    else:
                        if num != possibles:
                            self.possible_locations[num-1, i, j] = 0

        pass

    def check_possible_locations(self):

        locations_updated = False

        for row in range(self.size):
            for num in range(1, self.size+1):
                if self.possible_locations[num-1, row, :].sum() == 1:
                    col = np.where(self.possible_locations[num-1, row, :])[0]
                    self.grid.known_values[row, col] = num
                    self.grid.possible_values[row, col] = num
                    locations_updated = True
                    self.possible_locations[num-1, row, col] = 2

        for col in range(self.size):
            for num in range(1, self.size+1):
                if self.possible_locations[num-1, :, col].sum() == 1:
                    row = np.where(self.possible_locations[num-1, :, col])[0]
                    self.grid.known_values[row, col] = num
                    self.grid.possible_values[row, col] = num
                    locations_updated = True
                    self.possible_locations[num-1, row, col] = 2

        for box in range(1, self.size+1):
            for num in range(1, self.size+1):
                if self.possible_locations[num-1, :, :][self.grid.boxes == box].sum() == 1:
                    box_ind = np.where(self.grid.boxes == box)
                    cell_box_ind = np.where(self.possible_locations[num-1, :, :][self.grid.boxes == box])
                    row = box_ind[0][cell_box_ind[0]]
                    col = box_ind[1][cell_box_ind[0]]
                    self.grid.known_values[row, col] = num
                    self.grid.possible_values[row, col] = num
                    locations_updated = True
                    self.possible_locations[num-1, row, col] = 2

        return locations_updated

    def check_restricted_locations(self):

        locations_updated = False

        if self.grid.default_boxes:
            for row in range(self.size):
                for num in range(1, self.size + 1):
                    if (self.possible_locations[num - 1, row, :] == 1).sum() in range(2, self.box_size+1):
                        boxes = self.grid.boxes[row, self.possible_locations[num - 1, row, :] == 1]
                        if len(np.unique(boxes)) == 1:
                            for row2 in range(self.size):
                                if row2 != row:
                                    for col in range(self.size):
                                        if (isinstance(self.grid.possible_values[row2, col], list)) and \
                                                (self.grid.boxes[row2, col] == boxes[0]):
                                            if num in self.grid.possible_values[row2, col]:
                                                self.grid.possible_values[row2, col].remove(num)
                                                locations_updated = True
            for col in range(self.size):
                for num in range(1, self.size + 1):
                    if (self.possible_locations[num - 1, :, col] == 1).sum() in range(2, self.box_size+1):
                        boxes = self.grid.boxes[self.possible_locations[num - 1, :, col] == 1, col]
                        if len(np.unique(boxes)) == 1:
                            for col2 in range(self.size):
                                if col2 != col:
                                    for row in range(self.size):
                                        if (isinstance(self.grid.possible_values[row, col2], list)) and \
                                                (self.grid.boxes[row, col2] == boxes[0]):
                                            if num in self.grid.possible_values[row, col2]:
                                                self.grid.possible_values[row, col2].remove(num)
                                                locations_updated = True

            for box in range(1, self.size+1):
                for num in range(1, self.size + 1):
                    # For all possible locations in box, find how many rows/cols there are.
                    # If just 1, remove from non-box elements in that row/col
                    if (self.possible_locations[num-1, self.grid.boxes == box] == 1).sum() in range(2, self.box_size+1):
                        rows = np.where(self.grid.boxes == box)[0][
                            self.possible_locations[num-1, self.grid.boxes == box] == 1]
                        cols = np.where(self.grid.boxes == box)[1][
                            self.possible_locations[num-1, self.grid.boxes == box] == 1]
                        if len(np.unique(rows)) == 1:
                            for col in range(self.size):
                                if self.grid.boxes[rows[0], col] != box:
                                    if (isinstance(self.grid.possible_values[rows[0], col], list)):
                                        if num in self.grid.possible_values[rows[0], col]:
                                            self.grid.possible_values[rows[0], col].remove(num)
                                            locations_updated = True
                        if len(np.unique(cols)) == 1:
                            for row in range(self.size):
                                if self.grid.boxes[row, cols[0]] != box:
                                    if (isinstance(self.grid.possible_values[row, cols[0]], list)):
                                        if num in self.grid.possible_values[row, cols[0]]:
                                            self.grid.possible_values[row, cols[0]].remove(num)
                                            locations_updated = True

        return locations_updated
