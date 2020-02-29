#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 12:43:55 2019

@author: sqky
"""

from copy import deepcopy
from math import floor


def solve(input_grid):
    grid = deepcopy(input_grid)

    if predict(grid):
        return grid
    else:
        print('Solution does not exist.')


def predict(grid, row=0, col=0):
    # this place is empty (equal to 0)
    if grid[row][col] == 0:
        in_row = grid[row]
        in_col = [ grid[i][col] for i in range(9) ]
        in_box = [ grid[floor(row/3)*3 + i][floor(col/3)*3 + j] for i in range(3) for j in range(3) ]

        i = 1
        while i <= 9:
            # i is not in elsewhere in this row, column or box
            if i not in in_row and i not in in_col and i not in in_box:
                grid[row][col] = i
                next_pos_tuple = get_next_pos(row, col)
                if next_pos_tuple is None:
                    return True

                if predict(grid, next_pos_tuple[0], next_pos_tuple[1]):
                    return True
            # i is already somewhere in this row, column or box
            else:
                if i == 9:
                    grid[row][col] = 0
                    return False
                else:
                    i += 1
    # there is already a number in this place
    else:
        next_pos_tuple = get_next_pos(row, col)
        if next_pos_tuple is None:
            return True

        if predict(grid, next_pos_tuple[0], next_pos_tuple[1]):
            return True
        else:
            return False


def get_next_pos(row, col):
    if row == 8 and col == 8:
        return None
    else:
        next_col = col + 1
        if next_col > 8:
            next_row = row + 1
            next_col = 0
        else:
            next_row = row
        return next_row, next_col


def pos_out_of_grid(pos):
    if pos[1] > 8:
        return True
    else:
        return False


example_1 = [[3, 0, 6, 5, 0, 8, 4, 0, 0],
             [5, 2, 0, 0, 0, 0, 0, 0, 0],
             [0, 8, 7, 0, 0, 0, 0, 3, 1],
             [0, 0, 3, 0, 1, 0, 0, 8, 0],
             [9, 0, 0, 8, 6, 3, 0, 0, 5],
             [0, 5, 0, 0, 9, 0, 6, 0, 0],
             [1, 3, 0, 0, 0, 0, 2, 5, 0],
             [0, 0, 0, 0, 0, 0, 0, 7, 4],
             [0, 0, 5, 2, 0, 6, 3, 0, 0]]

example_2 = [[0, 0, 0, 0, 0, 0, 6, 8, 0],
             [0, 0, 0, 0, 7, 3, 0, 0, 9],
             [3, 0, 9, 0, 0, 0, 0, 4, 5],
             [4, 9, 0, 0, 0, 0, 0, 0, 0],
             [8, 0, 3, 0, 5, 0, 9, 0, 2],
             [0, 0, 0, 0, 0, 0, 0, 3, 6],
             [9, 6, 0, 0, 0, 0, 3, 0, 8],
             [7, 0, 0, 6, 8, 0, 0, 0, 0],
             [0, 2, 8, 0, 0, 0, 0, 0, 0]]


solution = solve(example_1)
for i in solution:
    print(i)

print()

solution = solve(example_2)
for i in solution:
    print(i)
