from python.Sudoku import Sudoku
from python.Grid import Grid
import numpy as np
import copy


class ClassicSudoku(Sudoku):

    def __init__(self, size=9, grid=None):
        super().__init__(size, grid)

    def check_solution(self, grid):
        # Check columns
        col_check = all([all([x in col for x in range(1, grid.size+1)]) for col in grid.known_values])

        # Check rows
        # grid_transpose = list(map(list, zip(*grid)))
        grid_transpose = grid.known_values.transpose()
        row_check = all([all([x in row for x in range(1, grid.size+1)]) for row in grid_transpose])

        # Check boxes
        box_check = all([all([x in grid.known_values[grid.boxes == box]
                              for x in range(1, grid.size+1)])
                         for box in range(1, grid.size+1)])

        return all([col_check, row_check, box_check])

    def check_intermediate(self, grid=None):
        if grid is None:
            grid = self.grid

        # Check columns
        col_check = all([len(set(x[x > 0])) == sum(x > 0) for x in grid.known_values])

        # Check rows
        grid_transpose = grid.known_values.transpose()
        row_check = all([len(set(x[x > 0])) == sum(x > 0) for x in grid_transpose])

        # Check boxes
        box_nums = np.array([[x for x in grid.known_values[grid.boxes == box]] for box in range(1, grid.size+1)])
        box_check = all([len(set(x[x > 0])) == sum(x > 0) for x in box_nums])

        # Check if any possibles are empty
        pos_check = all([all([len(y) > 0 for y in x if isinstance(y, list)]) for x in grid.possible_values])

        # Check if some numbers have nowhere to go in row, column or box
        loc_check_row, loc_check_col, loc_check_box = True, True, True
        for row in range(self.size):
            for num in range(1, self.size+1):
                if self.possible_locations[num-1, row, :].sum() == 0:
                    loc_check_row = False
        for col in range(self.size):
            for num in range(1, self.size+1):
                if self.possible_locations[num-1, :, col].sum() == 0:
                    loc_check_col = False
        for box in range(1, self.size+1):
            for num in range(1, self.size+1):
                if self.possible_locations[num-1, :, :][self.grid.boxes == box].sum() == 0:
                    loc_check_box = False

        loc_check = all([loc_check_row, loc_check_col, loc_check_box])

        return all([col_check, row_check, box_check, pos_check, loc_check])

    def step_solve(self):
        self.gen_possible_values()
        grid_changed = self.check_potential_values()
        self.gen_potential_location()
        if not grid_changed:
            grid_changed = self.check_possible_locations()
        if not grid_changed:
            grid_changed = self.multi_poss_values()
        if not grid_changed:
            grid_changed = self.check_restricted_locations()
        if not grid_changed:
            pass # grid_changed = self.find_removals(degree=1)
        return grid_changed

    def find_removals(self, degree=1):

        grid_changed = False
        grid_backup = self.grid.known_values.copy()
        possibles_backup = copy.deepcopy(self.grid.possible_values)

        # For degree=1:
        # - Loop over all cells
        # -- Loop over all possibles and run gen/check for value and locaton
        # --- If problem -> remove as option, and grid_changed = True

        for i in range(self.size):
            for j in range(self.size):
                if isinstance(self.grid.possible_values[i, j], list):
                    possibles = self.grid.possible_values[i, j].copy()
                    for possible in possibles:
                        self.grid.known_values[i, j] = possible
                        self.gen_possible_values()
                        self.check_potential_values()
                        self.gen_potential_location(full_check=True)
                        self.check_possible_locations()

                        if not self.check_intermediate(self.grid):
                            possibles_backup[i, j].remove(possible)
                            grid_changed = True

                        self.grid.known_values = grid_backup.copy()
                        self.grid.possible_values = copy.deepcopy(possibles_backup)

        return grid_changed

    def force_solve(self, level=1, done=0, target=1, max_level=None):

        # location = (np.where([self.grid.known_values == 0])[1][0], np.where([self.grid.known_values == 0])[2][0])
        index = np.argmin([len(x) for x in self.grid.possible_values[self.grid.known_values == 0]])
        location = (np.where([self.grid.known_values == 0])[1][index],
                    np.where([self.grid.known_values == 0])[2][index])
        possibles = self.grid.possible_values[location]
        grid_backup = self.grid.known_values.copy()
        if level > self.max_degree:
            self.max_degree = level
            print(f'New maximum degree of bifurcation: {level}')

        if len(possibles) == 0:
            print(f'New level is immediately empty. ({level})')

        done_increment = (target-done) / len(possibles)

        while len(possibles) > 0:
            self.grid.known_values[location] = possibles[0]
            if level <= 12:
                print(f'Try new option in: {location} as {possibles[0]} ({level}) from {possibles} ({np.round(done,5)})')
            # print(self.grid.known_values)
            self.gen_possible_values(full_check=True)
            grid_changed = self.step_solve()
            self.gen_potential_location(full_check=True)
            while grid_changed:
                # print(f'Updated grid to ({level}): \n' + str(self.grid.known_values))
                grid_changed = self.step_solve()
            if self.check_solution(self.grid):
                # print(f'Solution found!!!!!!!!!!!({level}) \n' + str(self.grid))
                return self.grid
            if not self.check_intermediate(self.grid):
                # print(f'Inconsistent puzzle, remove option and retry. ({level})')
                possibles = possibles[1:]
                # print(grid_backup)
                self.grid.known_values = grid_backup.copy()
                # print(self.grid.known_values)
                self.gen_possible_values(full_check=True)
                self.gen_potential_location(full_check=True)
            else:
                if max_level:
                    if max_level > 0:
                        result = self.force_solve(level=level + 1, done=done, target=done+done_increment,
                                                  max_level=max_level - 1)
                else:
                    result = self.force_solve(level=level + 1, done=done, target=done + done_increment)
                if result is False:
                    possibles = possibles[1:]
                    # print(f'Stepped back puzzle, remove option and retry. ({level})')
                    self.grid.known_values = grid_backup.copy()
                    # print(self.grid.known_values)
                    self.gen_possible_values(full_check=True)
                    self.gen_potential_location(full_check=True)
                else:
                    return result
            done += done_increment

        if self.check_solution(self.grid):
            # print(f'Solution found! ({level})')
            return self.grid
        else:
            # print(f'No solution found! ({level})')
            return False

    def multi_poss_values(self):

        updated = False

        for i_row in range(self.size):
            row = self.grid.possible_values[i_row]
            col = self.grid.possible_values[:, i_row]
            box = self.grid.possible_values[self.grid.boxes == i_row]
            for i in range(1, self.size + 1):
                for j in range(i + 1, self.size + 1):
                    if len(np.where([i in x and j in x and len(x) == 2 for x in row if isinstance(x, list)])[0]) == 2:
                        new_row = self.multi_poss_cell(i, j, row)
                        if isinstance(new_row, np.ndarray):
                            self.grid.possible_values[i_row] = new_row
                            updated = True
                    if len(np.where([i in x and j in x and len(x) == 2 for x in col if isinstance(x, list)])[0]) == 2:
                        new_col = self.multi_poss_cell(i, j, col)
                        if isinstance(new_col, np.ndarray):
                            self.grid.possible_values[:, i_row] = new_col
                            updated = True
                    if len(np.where([i in x and j in x and len(x) == 2 for x in box if isinstance(x, list)])[0]) == 2:
                        new_box = self.multi_poss_cell(i, j, box)
                        if isinstance(new_box, np.ndarray):
                            self.grid.possible_values[self.grid.boxes == i_row] = new_box
                            updated = True
        return updated

    def multi_poss_cell(self, i, j, cells):  # TODO: convert to more than 2 cells
        indices = np.where([i in x and j in x and len(x) == 2 if isinstance(x, list) else False for x in cells])[0]
        check_done = sum([(i in x and j in x) if isinstance(x, list) else False for x in cells])
        if len(indices) == 2 and check_done > 2:
            cells_new = np.array([[y for y in x if y not in (i, j)] if isinstance(x, list) else x for x in cells])
            for ind in indices:
                cells_new[ind] = list([i, j])
        else:
            cells_new = False
        return cells_new

    def solve(self):

        print('\nNew puzzle: \n' + str(self.grid.known_values))

        is_analytical = True
        intermediate = []
        intermediate_possibles = []
        solved = False

        self.gen_possible_values()
        grid_changed = self.step_solve()
        while grid_changed:
            grid_changed = self.step_solve()

        if self.check_solution(self.grid):
            print('Analytical solution found!')
            print(self.grid.known_values)
            solved = True
        else:
            print('Analytical solution not found. Resorting to bifurcation with intermediate grid:')
            print(self.grid.known_values)
            is_analytical = False
            intermediate = self.grid.known_values.copy()
            intermediate_possibles = self.grid.possible_values.copy()
            self.force_solve()
            if self.check_solution(self.grid):
                print('A solution found by trial and error!')
                print(self.grid.known_values)
                solved = True
            else:
                print('No solution found!')

        summary = {'grid': self.grid.known_values, 'analytical': is_analytical, 'intermediate': intermediate,
                   'solved': solved, 'max_degree': self.max_degree, 'intermediate_possibles': intermediate_possibles}

        return summary


if __name__ == "__main__":
    g = Grid(np.array([[1, 0, 3, 0],
                       [0, 0, 2, 0],
                       [3, 1, 0, 0],
                       [0, 0, 0, 0]]))
    puzzle = ClassicSudoku(grid=g)
    puzzle.solve()
