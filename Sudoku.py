#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 23:00:17 2019

@author: sqky
"""

import sys
from copy import deepcopy
from time import time, sleep
from random import choice, shuffle

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTime, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPainter, QPen


class SudokuWindow(QMainWindow):
	BLANK_STYLE = "QPushButton {  }"
	BLACK_BG = "QLabel { background-color: black }"
	BLUE_BORDER = "QPushButton { border: 2px solid #4476ff; border-radius: 5px; }"
	BLUE_TEXT = "QPushButton { color: #1B37FF; }"
	BOTTOM_BAR_PICTURE = 'QLabel { background: url("images/wp3.jpg") }'
	COLLIDER = "QPushButton { background-color: #73c7ff; border: 3px solid red; border-radius: 3px; }"
	CURRENT_ACTIVE_CHOICE_BUTTON = "QPushButton { border: 2px solid #4476ff; border-radius: 5px; }"
	CURRENT_INACTIVE_CHOICE_BUTTON = "QPushButton { background-color: #bbbbbb; }"
	FOOTER_BAR = "QLabel { background-color: #2f2f2f; color: #ebebeb; text-align: center; font-size: 13px; }"
	GREEN_BORDER_BLUE_TEXT = "QPushButton { color: #1B37FF; border: 2px solid #85ff42 }"
	HIGHLIGHT_STARTERS = "QPushButton { background-color: #8CB164 }"
	HIGHLIGHT_CHOICES = "QPushButton { background-color: #D8FF9C }"
	HINTS_DEFAULT = "QPushButton { color: #1B37FF; }"
	LIMITING_FIELDS = "QPushButton { background-color: #73c7ff }"
	LIMITING_HINTS = "QPushButton { color: #1B37FF; background-color: #73c7ff }"
	OTHER_ACTIVE_CHOICE_BUTTON = BLANK_STYLE
	OTHER_INACTIVE_CHOICE_BUTTON = "QPushButton { background-color: #cccccc; }"
	PREDEFINED_GAME_TILE = "QPushButton { background-color: #b2b2b2 }"
	STARTERS_DEFAULT = "QPushButton { background-color: #b2b2b2 }"
	TOP_BAR_BG = "QLabel { background-color: #e5e5e5 }"
	TOP_BAR_BUTTONS = "QPushButton { background-color: #a1a1a1; font-size: 18px; font-weight: bold; }"
	WHITE_BG = "QPushButton { background-color: white }"

	def __init__(self, width=450, height=600, screen_size=(1366, 768)):
		super().__init__()
		self.width = width
		self.height = height
		self.screen_size = screen_size
		self.setWindowTitle('Sudoku Go!')

		self.current_number = 0
		self.fields = []
		self.choice_buttons = []
		self.note_mode = False
		self.backlog = []  # User action history [(field_id, field, value_before, value_after)]

		self.solved = None
		self.unsolved = None
		self.unsolved_cast = None
		self.missing_values_amount = None
		self.filled_digits = {x: 0 for x in range(1, 9+1)}
		self.hint_filled_ids = []

		self.current_field_id = None
		self.current_row = None
		self.current_col = None
		self.current_box = None
		self.current_area = None

		self.used_help = False

	def get_grids(self, grids):
		self.solved = grids[0]
		self.unsolved = grids[1]
		self.unsolved_cast = [x for x in range(len(self.unsolved)) if self.unsolved[x] != 0]
		for i in self.unsolved_cast:
			self.filled_digits[self.unsolved[i]] += 1
		self.missing_values_amount = 81 - len(self.unsolved_cast)

	def set_window_size(self):
		width_factor = int((self.screen_size[0] - self.width) / 2)
		height_factor = int((self.screen_size[1]-self.height)/2)
		self.setGeometry(width_factor, height_factor, self.width, self.height)
		self.setWindowIcon(QIcon('images/icon.png'))

	def generate_view(self, grid=None):
		# set menu bar
		menu_bar = QtWidgets.QLabel(self)
		menu_bar.setGeometry(0, 0, self.width, 60)
		menu_bar.setStyleSheet(self.TOP_BAR_BG)

		menu_button_width = 150
		menu_button_height = 40
		margin = (menu_bar.height() - menu_button_height)/2
		# hint button
		hint_button = QtWidgets.QPushButton('Hint', menu_bar)
		hint_button.setToolTip('Reveal one number')
		hint_button.resize(menu_button_width, menu_button_height)
		hint_button.move(int(margin), int(margin))
		hint_button.clicked.connect(self.get_hint)

		# undo button
		undo_button = QtWidgets.QPushButton('Undo', menu_bar)
		undo_button.setToolTip('Undo your previous move')
		undo_button.resize(menu_button_width, menu_button_height)
		undo_button.move(int(self.width-menu_button_width-margin), int(margin))
		undo_button.clicked.connect(self.undo_move)
		self.setStyleSheet(self.TOP_BAR_BUTTONS)

		# game grid
		field_size = self.width/9
		grid = QtWidgets.QLabel(self)
		grid.setGeometry(0, menu_bar.height(), 450, 450)
		grid.setStyleSheet(self.WHITE_BG)

		for i in range(81):
			field = QtWidgets.QPushButton(str(self.unsolved[i]) if self.unsolved[i] != 0 else '', grid)
			field.setGeometry(int((i % 9*field_size)), int((i//9*field_size)), int(field_size), int(field_size))
			field.clicked.connect(self.update_current_area)
			field.clicked.connect(self.highlight_resonations)
			if i in self.unsolved_cast:
				field.setStyleSheet(self.PREDEFINED_GAME_TILE)
			else:
				field.clicked.connect(self.field_click)
			self.fields.append(field)

		line_thickness = 2
		for x in range(2):
			v_bar = QtWidgets.QLabel(grid)
			v_bar.setGeometry(int(x*grid.width()/3+3*field_size-line_thickness/2), 0, line_thickness, grid.height())
			v_bar.setStyleSheet(self.BLACK_BG)
			h_bar = QtWidgets.QLabel(grid)
			h_bar.setGeometry(0, int(x*grid.height()/3+3*field_size-line_thickness/2), grid.width(), line_thickness)
			h_bar.setStyleSheet(self.BLACK_BG)

		# number choice bar
		num_bar = QtWidgets.QLabel(window)
		num_bar.setGeometry(0, menu_bar.height()+grid.height(), self.width, 70)
		num_bar.setStyleSheet(self.BOTTOM_BAR_PICTURE)
		choice_button_size = num_bar.width() // 11
		for i in range(1, 1+11):
			choice_button = QtWidgets.QPushButton(str(i) if i < 10 else '', num_bar)
			choice_button_h_offset = (i-1)*choice_button_size+(self.width % 12)-1
			choice_button_v_offset = int((num_bar.height()-choice_button_size)/2)
			choice_button.setGeometry(choice_button_h_offset, choice_button_v_offset, choice_button_size-1, choice_button_size)
			if i <= 9:
				choice_button.clicked.connect(self.update_current_number)
			elif i == 10:
				choice_button.clicked.connect(self.rubber)
				choice_button.setIcon(QIcon('images/rubber.png'))
				choice_button.setIconSize(QSize(int(.8*choice_button_size), int(.8*choice_button_size)))
			else:
				choice_button.clicked.connect(self.note)
			self.choice_buttons.append(choice_button)
		self.update_missing_digits()

		# footer
		footer = QtWidgets.QLabel(window)
		footer.setGeometry(0, menu_bar.height()+grid.height()+num_bar.height(), self.width, 20)
		footer.setStyleSheet(self.FOOTER_BAR)
		footer.setText("Sudoku by Paweł Wacławiak ©")
		footer.setAlignment(Qt.AlignCenter)

	def highlight_restrictions(self, blue_highlighted=None):
		try:
			for x in self.current_area:
				if self.fields[x].text() != blue_highlighted:
					if x in self.unsolved_cast:
						self.fields[x].setStyleSheet(self.HIGHLIGHT_STARTERS)
					else:
						self.fields[x].setStyleSheet(self.HIGHLIGHT_CHOICES)
		except TypeError:
			pass

	def highlight_resonations(self):
		try:
			number = self.current_number
		except ValueError:
			pass
		self.highlight_number(number)
		self.highlight_restrictions(str(number))

	def highlight_number(self, number):
		number = str(number)
		print('number: {}   curr_num: {}'.format(number, self.current_number))
		for x in range(len(self.fields)):
			if self.fields[x].text() == number:
				if x in self.hint_filled_ids:
					self.fields[x].setStyleSheet(self.LIMITING_HINTS)
				else:
					self.fields[x].setStyleSheet(self.LIMITING_FIELDS)
			else:
				if x in self.unsolved_cast:
					self.fields[x].setStyleSheet(self.STARTERS_DEFAULT)
				else:
					if x in self.hint_filled_ids:
						self.fields[x].setStyleSheet(self.HINTS_DEFAULT)
					else:
						self.fields[x].setStyleSheet(self.WHITE_BG)

	def field_click(self):
		if self.current_number:
			previous_number = self.unsolved[self.current_field_id]
			if self.current_number != previous_number:
				restricted = set([int(self.fields[num].text()) for num in self.current_area if self.fields[num].text()])
				if self.current_number not in restricted:
					self.add_to_history(self.current_field_id, self.sender(), previous_number, self.current_number)
					if self.unsolved[self.current_field_id] != 0:  # If the field was not empty do not decrease the counter
						self.filled_digits[previous_number] -= 1  # Decrease the previous number count
					else:
						self.missing_values_amount -= 1
					self.sender().setText(str(self.current_number))
					self.unsolved[self.current_field_id] = self.current_number
					self.filled_digits[self.current_number] += 1
					self.sender().setStyleSheet(self.BLUE_BORDER)
					self.choice_buttons[self.current_number-1].setStyleSheet(self.CURRENT_ACTIVE_CHOICE_BUTTON)
					if not self.missing_values_amount:
						self.check_for_win()
				else:  # Highlighting colliding numbers with red border
					if self.current_number != 0:
						ids = [i for i in self.current_area if self.fields[i].text() == str(self.current_number)]
						for index in ids:
							self.fields[index].setStyleSheet(self.COLLIDER)
		else:  # Erasing with a rubber
			try:
				number = int(self.sender().text())
				self.add_to_history(self.current_field_id, self.sender(), self.unsolved[self.current_field_id], self.current_number)
				self.filled_digits[number] -= 1
				self.missing_values_amount += 1
				self.unsolved[self.current_field_id] = self.current_number
				self.sender().setText('')
			except ValueError:
				pass
		self.update_missing_digits()
		print(self.missing_values_amount)

	def add_to_history(self, field_id, field, before, after):
		if before != after:
			self.backlog.append((field_id, field, before, after))
			print(self.backlog[-1])

	def check_for_win(self):
		success = True
		for x in range(81):
			if self.unsolved[x] != self.solved[x]:
				success = False
		if success:
			print('You won!\n')

	def update_missing_digits(self):
		for digit in range(1, 9+1):
			if self.filled_digits[digit] == 9:
				self.choice_buttons[digit - 1].setEnabled(False)
				if digit == self.current_number:
					self.choice_buttons[digit-1].setStyleSheet(self.CURRENT_INACTIVE_CHOICE_BUTTON)
				else:
					self.choice_buttons[digit-1].setStyleSheet(self.OTHER_INACTIVE_CHOICE_BUTTON)

			else:
				self.choice_buttons[digit-1].setEnabled(True)
				if digit == self.current_number:
					self.choice_buttons[digit-1].setStyleSheet(self.CURRENT_ACTIVE_CHOICE_BUTTON)
				else:
					self.choice_buttons[digit-1].setStyleSheet(self.BLANK_STYLE)

	def update_current_number(self):
		"""
		Updates the currently chosen number to be filled into cells
		:return:
		"""
		try:
			number = int(self.sender().text())
			self.current_number = number
		except ValueError:
			pass
		finally:
			self.highlight_number(self.current_number)
			self.update_missing_digits()
			self.choice_buttons[9].setStyleSheet(self.BLANK_STYLE)

	def rubber(self):
		self.current_number = 0
		self.update_current_number()
		self.sender().setStyleSheet(self.BLUE_BORDER)
		self.highlight_number(0)

	def note(self):
		self.note_mode = False if self.note_mode else True
		print(self.note_mode)

	def get_hint(self):
		self.used_help = True
		possible_cells = [x for x in range(81) if self.unsolved[x] != self.solved[x]]
		chosen_id = choice(possible_cells)
		self.unsolved[chosen_id] = self.solved[chosen_id]
		self.missing_values_amount -= 1
		self.filled_digits[self.solved[chosen_id]] += 1
		self.fields[chosen_id].setText(str(self.solved[chosen_id]))
		self.fields[chosen_id].setStyleSheet(self.GREEN_BORDER_BLUE_TEXT)
		self.hint_filled_ids.append(chosen_id)
		self.update_missing_digits()
		self.check_for_win()

	def undo_move(self):
		try:
			move = self.backlog.pop()

			print(move)
			print('backlog length = {}'.format(len(self.backlog)))

			(field_id, field, value_before, value_after) = move
			self.unsolved[field_id] = value_before
			field.setText(str(value_before or ''))
			try:
				self.filled_digits[value_before] += 1
				self.filled_digits[value_after] -= 1
			except KeyError:
				pass
			if value_before != 0 and value_after == 0:
				self.missing_values_amount -= 1
			if value_before == 0 and value_after != 0:
				self.missing_values_amount += 1

			# TODO un-highlight cell after undo
				# self.current_field_id = None
		except IndexError:
			pass
		finally:
			self.update_missing_digits()
			self.highlight_resonations()
			print(self.missing_values_amount)

	def update_current_area(self):
		field_id = [x for x in range(81) if self.fields[x] == self.sender()].pop()
		self.current_field_id = field_id
		self.current_row = [x for x in range(field_id-field_id % 9, field_id//9*9+9)]
		self.current_col = [x*9+field_id % 9 for x in range(9)]
		self.current_box = [range(81)[field_id//27*27 + field_id % 9//3*3 + x + y*9] for y in range(3) for x in range(3)]
		self.current_area = set(self.current_row + self.current_col + self.current_box)

	def show_window(self):
		self.update()
		self.show()


class Sudoku:

	def __init__(self, difficulty='easy'):
		self.grid = [0 for _ in range(81)]
		self.player_grid = []
		# self.player_grid = remove_values(difficulty)

		self.record = 0
		self.time = 0
		self.counter = 0
		pass

	def get_grids(self):
		return self.grid, self.player_grid

	def generate_grid(self):
		self._guess_field_value()
		return self.grid

	def _get_possible_inputs(self, field):
		"""
		Returns IDs of the cells that react with the one of ID given in terms of possible inputs to the cell.
		:param field: ID of a cell to figure out the other cells limiting its input.
		:return: Possible inputs to the specified cell.
		"""
		row = self.grid[field-field % 9: field//9*9+9]
		col = [self.grid[x*9+field % 9] for x in range(9)]
		trow = field//27  # thick_row - block of rows
		tcol = field % 9//3  # thick_col - block of columns
		box = [self.grid[trow*27+tcol*3+x+y*9] for y in range(3) for x in range(3)]

		possibilities = [x for x in range(0+1, 9+1) if x not in row and x not in col and x not in box]
		shuffle(possibilities)
		return possibilities

	def _guess_field_value(self, field=0):
		possibilities = self._get_possible_inputs(field)
		for current_choice in possibilities:
			self.grid[field] = current_choice

			if field == 80:
				return True

			if self._guess_field_value(field+1):
				return True

		# backtrace
		self.grid[field] = 0
		return False

	def solve_grid(self, field=0):
		if self.grid[field] == 0:
			possibilities = self._get_possible_inputs(field)
			# print(possibilities)
			for current_choice in possibilities:
				self.grid[field] = current_choice

				if field == 80:
					self.grid[field] = 0
					return True

				if self.solve_grid(field+1):
					self.grid[field] = 0
					return True

			# BACKTRACE
			self.grid[field] = 0
			return False

		elif field == 80:
			return True
		else:
			return self.solve_grid(field+1)

	def prepare_grid(self, difficulty='easy'):
		ready = False
		attempt = 1
		while not ready:
			base_grid = [x for x in self.grid]
			print('attempt: ', attempt)
			ready = self.remove_values(difficulty)
			if not ready:
				self.grid = [x for x in base_grid]
				attempt += 1

	def remove_values(self, difficulty='easy'):
		quantities = {1: 9, 2: 9, 3: 9, 4: 9, 5: 9, 6: 9, 7: 9, 8: 9, 9: 9}
		emptied = False
		goal = 0
		if difficulty == 'easy':
			goal = 40
		if difficulty == 'medium':
			goal = 34
		if difficulty == 'hard':
			goal = 28
		removed = []

		fail_count = 0
		base_grid = deepcopy(self.grid)

		while len(removed) < 81-goal:
			rm1 = choice([x for x in range(81) if x not in removed])
			rm2 = 80 - rm1
			num1 = self.grid[rm1]
			num2 = self.grid[rm2]

			if rm1 == rm2:
				if quantities[num1] > 1:
					self.grid[rm1] = 0
					if self.single_solution_check(base_grid):
						removed.append(rm1)
						quantities[num1] -= 1
					else:
						self.grid[rm1] = num1
						fail_count += 1
				elif not emptied:
					self.grid[rm1] = 0
					if self.single_solution_check(base_grid):
						removed.append(rm1)
						quantities[num1] -= 1
						emptied = True
					else:
						self.grid[rm1] = num1
						fail_count += 1
				# continue
			else:
				if num1 != num2:
					if quantities[num1] > 1 and quantities[num2] > 1:
						self.grid[rm1] = 0
						self.grid[rm2] = 0
						if self.single_solution_check(base_grid):
							removed.append(rm1)
							removed.append(rm2)
							quantities[num1] -= 1
							quantities[num1] -= 1
						else:
							self.grid[rm1] = num1
							self.grid[rm2] = num2
							fail_count += 1
					elif not emptied and quantities[num1] != quantities[num2]:
						self.grid[rm1] = 0
						self.grid[rm2] = 0
						if self.single_solution_check(base_grid):
							removed.append(rm1)
							removed.append(rm2)
							quantities[num1] -= 1
							quantities[num1] -= 1
							emptied = True
						else:
							self.grid[rm1] = num1
							self.grid[rm2] = num2
							fail_count += 1
					# continue
				else:
					if quantities[num1] > 2:
						self.grid[rm1] = 0
						self.grid[rm2] = 0
						if self.single_solution_check(base_grid):
							removed.append(rm1)
							removed.append(rm2)
							quantities[num1] -= 2
						else:
							self.grid[rm1] = num1
							self.grid[rm2] = num1
							fail_count += 1
					elif not emptied and quantities[num1] == 2:
						self.grid[rm1] = 0
						self.grid[rm2] = 0
						if self.single_solution_check(base_grid):
							removed.append(rm1)
							removed.append(rm2)
							quantities[num1] -= 2
							emptied = True
						else:
							self.grid[rm1] = num1
							self.grid[rm2] = num1
							fail_count += 1
					# continue
			if fail_count >= 10:
				return False

		self.player_grid = self.grid
		self.grid = base_grid
		return True

	def single_solution_check(self, solved_grid):
		for i in range(5):
			if not self.human_solve(solved_grid):
				return False

		grid = [x for x in self.grid]

		for i in range(3):
			single_solution = self.solve_grid()
			self.grid = [x for x in grid]
			if not single_solution:
				return False

		return True

	def human_solve(self, solved_grid):
		grid = [x for x in self.grid]
		# options = {x:[] for x in range(81) if not grid[x]}
		# for x in options:
		# 	row = grid[x-x%9 : x//9*9+9]
		# 	col = [grid[x*9+x%9] for x in range(9)]
		# 	box = [grid[x//27*27+x%9//3*3+a+b*9] for b in range(3) for a in range(3)]
		# 	forbidden_digits = set(grid[i] for i in row+col+box)
		# 	options[x] = [n for n in range(1, 9+1) if n not in forbidden_digits]
		# 	if not options[x]:
		# 		return False

		# for x in options:
		# 	row = grid[x-x%9 : x//9*9+9]
		# 	col = [grid[x*9+x%9] for x in range(9)]
		# 	box = [grid[x//27*27+x%9//3*3+a+b*9] for b in range(3) for a in range(3)]
		# 	related_indexes = list( set(row + col + box) )
		# 	for y in options[x]:
		# 		others = []
		# 		others = others + inner for inner in related_indexes
		# 		if y not in others:  # the only suitable place for number y
		# 			# TODO: assign y to the index
		# 			pass



		# row = self.grid[field-field % 9 : field//9*9+9]
		# col = [self.grid[x*9+field%9] for x in range(9)]
		# trow = field//27  # thick_row - block of rows
		# tcol = field%9//3  # thick_col - block of collumns
		# box = [self.grid[trow*27+tcol*3+x+y*9] for y in range(3) for x in range(3)]

		# prints with color
		# for x in range(9):
		# 	buffer = ''
		# 	for y in range(9):
		# 		num = grid[9*x + y]
		# 		if not num:
		# 			buffer += '\x1b[1;40;31m' + str(num) + '\x1b[0m '
		# 		else:
		# 			buffer += str(num) + ' '
		# 	print(buffer)

		# initializes options with 1-9 digits for fields that contain 0
		options = {x: list(range(1, 9+1)) for x in range(81) if not grid[x]}
		field_relations = {}
		solved_fields = []
		# for every empty field (containing 0)
		for field in options:
			# calculating related indexes
			row = list(range(field-field % 9, field//9*9+9))
			col = [x*9+field % 9 for x in range(9)]
			box = [field//27*27+field % 9//3*3+a+b*9 for b in range(3) for a in range(3)]
			related_indexes = list(set(row + col + box))

			# debug
			# for x in range(9):
			# 	buffer = ''
			# 	for y in range(9):
			# 		num = grid[9*x + y]
			# 		if not num:
			# 			buffer += '\x1b[1;40;31m' + str(num) + '\x1b[0m '
			# 		elif x*9+y in related_indexes:
			# 			buffer += '\x1b[1;40;32m' + str(num) + '\x1b[0m '
			# 		else:
			# 			buffer += str(num) + ' '
			# 	print(buffer)
			# print()
			#########################

			field_relations[field] = related_indexes
			for cell in related_indexes:
				if grid[cell] in options[field]:
					options[field].remove(grid[cell])

		# debug
		# for x in range(9):
		# 	buffer = ''
		# 	for y in range(9):
		# 		num = grid[9*x + y]
		# 		if not num:
		# 			buffer += '\x1b[1;40;31m' + str(num) + '\x1b[0m '
		# 		elif x*9+y in related_indexes:
		# 			buffer += '\x1b[1;40;32m' + str(num) + '\x1b[0m '
		# 		else:
		# 			buffer += str(num) + ' '
		# 	print(buffer)
		# print()

		# list of boxes (lists) containing field ids
		box_ids = [[(27*ver+3*hor)//27*27+(27*ver+3*hor) % 9//3*3+a+b*9 for b in range(3) for a in range(3)] for hor in range(3) for ver in range(3)]

		while 0 in grid:
			options_ref = deepcopy(options)

			# inferring in every box
			for box in box_ids:
				self.infer_in_box(options, box_ids, box)

			for field in options.keys():
				if not len(options[field]):
					print('Incorrect solution. Lacking further options for the field.', field)
					print(options)
					for x in range(9):
						buffer = ''
						for y in range(9):
							num = grid[9*x + y]
							if not num:
								buffer += '\x1b[1;40;31m' + str(num) + '\x1b[0m '
							elif x*9+y in related_indexes:
								buffer += '\x1b[1;40;32m' + str(num) + '\x1b[0m '
							else:
								buffer += str(num) + ' '
						print(buffer)
					print()
					return False

				if len(options[field]) == 1:
					grid[field] = options[field][0]

					# removing the option from related fields
					for related in field_relations[field]:
						if related in options.keys() and related != field:
							try:
								options[related].remove(grid[field])
							except (ValueError):
								pass
					solved_fields.append(field)

			for solved in solved_fields:
				try:
					options.pop(solved)
				except KeyError:
					pass

			if options == options_ref:  # this is smart enough to compare structures like list
				return False

		for index in range(81):
			if grid[index] != solved_grid[index]:
				print('cos sie ryplo i wyszlo zle rozwiazanie')
				return False

		return True

	# checking if all possibilities for a number in a specific box are aligned
	# if so, removing from respective row/col of other boxes options
	def infer_in_box(self, options, box_ids, box):
		for num in range(1,9+1):
			occurs = [index for index in box if (index in options.keys() and num in options[index])]

			if len(occurs) > 1:
				aligned_col = True
				aligned_row = True
				base_col = [x*9+occurs[0]%9 for x in range(9)]
				base_row = range(occurs[0]-occurs[0]%9, occurs[0]//9*9+9)
				for field in occurs[1:]:
					if [x*9+field%9 for x in range(9)] != base_col:
						aligned_col = False
					if range(field-field%9, field//9*9+9) != base_row:
						aligned_row = False

				if aligned_col:
					# print('options aligned in col')
					for field in base_col:
						if field not in box:
							try:
								options[field].remove(num)
								# no idea what this was for xd
								# changed_boxes.append(changed_box for changed_box in box_ids if options[field] in changed_box if changed_box not in changed_boxes)
							except (KeyError, ValueError):
								pass

				if aligned_row:
					# print('options aligned in row')
					for field in base_row:
						if field not in box:
							try:
								options[field].remove(num)
							except (KeyError, ValueError):
								pass

	def print_solo_grid(self, select='solved'):
		if select == 'solved':
			for i in range(9):
				buffer = ''
				for j in range(9):
					buffer += str(self.grid[i*9+j]) + ' '
				print(buffer)
		elif select == 'player':
			for i in range(9):
				buffer = ''
				for j in range(9):
					buffer += str(self.player_grid[i*9+j]) + ' '
				print(buffer)
		else:
			print('This feature is not implemented.')

	def print_both_grids(self):
		for i in range(9):
			buffer = ''
			for j in range(9):
				buffer += str(self.grid[i*9+j]) + ' '
			buffer += '  |  '
			for j in range(9):
				buffer += str(self.player_grid[i*9+j]) + ' '
			print(buffer)


if __name__ == '__main__':
	app = QApplication(sys.argv)

	sudoku = Sudoku()
	sudoku.generate_grid()
	sudoku.prepare_grid()

	window = SudokuWindow()
	window.get_grids(sudoku.get_grids())
	window.set_window_size()
	window.generate_view()
	window.show_window()
	sys.exit(app.exec_())

