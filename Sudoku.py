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

	def __init__(self):
		super().__init__()
		self.setWindowTitle('Sudoku Go!')
		self.current_choice = 0
		self.fields = []
		self.choice_buttons = []
		self.note_mode = False
		
		self.solved = None
		self.unsolved = None
		self.unsolved_cast = None
		self.missing_values_amount = None
		self.filled_digits = {x:0 for x in range(1,9+1)}

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

	def set_window_size(self, width=450, height=600, screen_size=[1366, 768]):
		self.setGeometry( (screen_size[0]-width)/2, (screen_size[1]-height)/2, width, height )
		self.setWindowIcon(QIcon('images/icon.png'))
		self.width = width
		self.height = height

	def generate_view(self, grid=None):
		# set menu bar
		menu_bar = QtWidgets.QLabel(self)
		menu_bar.setGeometry(0, 0, self.width, 60)
		menu_bar.setStyleSheet("QLabel { background-color: #e5e5e5 }")

		menu_button_width = 150
		menu_button_height = 40
		margin = (menu_bar.height() - menu_button_height)/2
		# hint button
		hint_button = QtWidgets.QPushButton('Hint', menu_bar)
		hint_button.setToolTip('Reveal one number')
		hint_button.resize(menu_button_width, menu_button_height)
		hint_button.move(margin, margin)
		hint_button.clicked.connect(self.get_hint)

		# undo button
		undo_button = QtWidgets.QPushButton('Undo', menu_bar)
		undo_button.setToolTip('Undo your previous move')
		undo_button.resize(menu_button_width, menu_button_height)
		undo_button.move(self.width-menu_button_width-margin, margin)
		self.setStyleSheet("QPushButton { background-color: #a1a1a1; font-size: 18px; font-weight: bold; }")

		# game grid
		field_size = (self.width)/9
		grid = QtWidgets.QLabel(self)
		grid.setGeometry(0, menu_bar.height(), 450, 450)
		grid.setStyleSheet("QPushButton { background-color: white }")

		for i in range(81):
			field = QtWidgets.QPushButton(str(self.unsolved[i]) if self.unsolved[i] != 0 else '', grid)
			field.setGeometry( (i%9*field_size), (i//9*field_size), field_size, field_size )
			field.clicked.connect(self.update_current_area)
			field.clicked.connect(self.highlight_resonations)
			if i in self.unsolved_cast:
				field.setStyleSheet("QPushButton { background-color: #b2b2b2 }")
				# field.clicked.connect(self.highlight_resonations)
			else:
				field.clicked.connect(self.field_click)
				# field.clicked.connect(self.highlight_restrictions)
			self.fields.append(field)

		line_thickness = 2
		for x in range(2):
			v_bar = QtWidgets.QLabel(grid)
			v_bar.setGeometry(x*grid.width()/3+3*field_size-line_thickness/2, 0, line_thickness, grid.height())
			v_bar.setStyleSheet("QLabel { background-color: black }")
			h_bar = QtWidgets.QLabel(grid)
			h_bar.setGeometry(0, x*grid.height()/3+3*field_size-line_thickness/2, grid.width(), line_thickness)
			h_bar.setStyleSheet("QLabel { background-color: black }")

		# number choice bar
		num_bar = QtWidgets.QLabel(window)
		num_bar.setGeometry(0, menu_bar.height()+grid.height(), self.width, 70)
		num_bar.setStyleSheet('QLabel { background: url("images/wp3.jpg") }')
		choice_button_size = num_bar.width() // 11
		for i in range(1, 1+11):
			choice_button = QtWidgets.QPushButton(str(i) if i < 10 else '', num_bar)
			choice_button.setGeometry((i-1)*choice_button_size+(self.width%12)-1, (num_bar.height()-choice_button_size)/2, choice_button_size-1, choice_button_size)
			if i <= 9:
				choice_button.clicked.connect(self.update_current_choice)
			elif i == 10:
				choice_button.clicked.connect(self.rubber)
				choice_button.setIcon(QIcon('images/rubber.png'))
				choice_button.setIconSize(QSize(.8*choice_button_size, .8*choice_button_size))
			else:
				choice_button.clicked.connect(self.note)
			self.choice_buttons.append(choice_button)
		self.update_missing_digits()

		# footer
		footer = QtWidgets.QLabel(window)
		footer.setGeometry(0, menu_bar.height()+grid.height()+num_bar.height(), self.width, 20)
		footer.setStyleSheet("QLabel { background-color: #2f2f2f; color: #ebebeb; text-align: center; font-size: 13px; }")
		footer.setText("Sudoku by Paweł Wacławiak ©")
		footer.setAlignment(Qt.AlignCenter)

	def highlight_restrictions(self, bool, blue_highlighted=None):
		for x in self.current_area:
			if self.fields[x].text() != blue_highlighted:
				if x in self.unsolved_cast:
					self.fields[x].setStyleSheet("QPushButton { background-color: #a1a162 }")
				else:
					self.fields[x].setStyleSheet("QPushButton { background-color: #ffff8c }")

	def highlight_resonations(self):
		if self.sender().text() and self.current_choice != 0:
			number = int(self.sender().text())
		else:
			number = self.current_choice
		self.highlight_number(number)
		self.highlight_restrictions(False, blue_highlighted=str(number))

	def highlight_number(self, number):
		for x in range(len(self.fields)):
			if self.fields[x].text() == str(number):
				self.fields[x].setStyleSheet("QPushButton { background-color: #73c7ff }")
			else:
				if x in self.unsolved_cast:
					self.fields[x].setStyleSheet("QPushButton { background-color: #b2b2b2 }")
				else:
					self.fields[x].setStyleSheet("QPushButton { background-color: white }")

	def field_click(self):
		if self.current_choice:
			restricted = set([int(self.fields[num].text()) for num in self.current_area if self.fields[num].text()])
			if self.current_choice not in restricted:
				self.sender().setText(str(self.current_choice))
				self.sender().setStyleSheet("QPushButton { background-color: #73c7ff }")
				self.unsolved[self.current_field_id] = self.current_choice
				self.filled_digits[self.current_choice] += 1
				self.update_missing_digits()
				self.missing_values_amount -= 1
				if not self.missing_values_amount:
					self.check_for_win()
			else:
				if self.current_choice != 0:
					ids = [i for i in self.current_area if self.fields[i].text() == str(self.current_choice)]
					for index in ids:
						self.fields[index].setStyleSheet("QPushButton { background-color: #73c7ff; border: 3px solid red; border-radius: 3px; }")
		else:
			number = int(self.sender().text())
			self.filled_digits[number] -= 1
			self.missing_values_amount += 1
			self.update_missing_digits()
			self.sender().setText('')
		print(self.missing_values_amount)

	def check_for_win(self):
		success = True
		for x in range(81):
			if self.unsolved[x] != self.solved[x]:
				success = False
		if success:
			print('You won!\n')

	def update_missing_digits(self):
		for digit in range(1,9+1):
			if self.filled_digits[digit] == 9:
				self.choice_buttons[digit-1].setEnabled(False)
				self.choice_buttons[digit-1].setStyleSheet("QPushButton {background-color: #cccccc}")
			else:
				self.choice_buttons[digit-1].setEnabled(True)
				self.choice_buttons[digit-1].setStyleSheet("QPushButton {  }")

	def update_current_choice(self):
		text = self.sender().text()
		self.update_missing_digits()
		for i in range(9, len(self.choice_buttons)):
			self.choice_buttons[i].setStyleSheet("QPushButton {  }")
		self.sender().setStyleSheet("QPushButton { border: 2px solid #4476ff; border-radius: 5px; }")
		try:
			number = int(text)
			self.current_choice = number
			self.highlight_number(number)
		except ValueError:
			pass

	def rubber(self):
		self.current_choice = 0
		for btn in self.choice_buttons:
			btn.setStyleSheet("QPushButton {  }")
		self.sender().setStyleSheet("QPushButton { border: 2px solid #4476ff; border-radius: 5px; }")
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
		self.fields[chosen_id].setStyleSheet("QPushButton { border: 2px solid #85ff42 }")
		self.update_missing_digits()
		self.check_for_win()

	def update_current_area(self):
		field_id = [x for x in range(81) if self.fields[x] == self.sender()].pop()
		self.current_field_id = field_id
		self.current_row = [x for x in range(field_id-field_id%9, field_id//9*9+9)]
		self.current_col = [x*9+field_id%9 for x in range(9)]
		self.current_box = [range(81)[field_id//27*27 + field_id%9//3*3 + x + y*9] for y in range(3) for x in range(3)]
		self.current_area = set(self.current_row + self.current_col + self.current_box)

	def show_window(self):
		self.update()
		self.show()


class Sudoku:

	def __init__(self, difficulty='easy'):
		self.grid = [0 for x in range(81)]
		self.player_grid = []
		# self.player_grid = remove_values(difficulty)

		self.record = 0
		self.time = 0
		self.counter = 0
		pass

	def get_grids(self):
		return (self.grid, self.player_grid)

	def generate_grid(self):
		self._guess_field_value()
		return self.grid

	def _guess_field_value(self, field=0):
		# figure out the limitating cells
		row = self.grid[field-field%9 : field//9*9+9]
		col = [self.grid[x*9+field%9] for x in range(9)]
		trow = field//27  # thick_row - block of rows
		tcol = field%9//3  # thick_col - block of collumns
		box = [self.grid[trow*27+tcol*3+x+y*9] for y in range(3) for x in range(3)]

		# limit possible inputs
		possibilities = [x for x in range(0+1,9+1) if x not in row and x not in col and x not in box]
		shuffle(possibilities)

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
			row = self.grid[field-field%9 : field//9*9+9]
			col = [self.grid[x*9+field%9] for x in range(9)]
			trow = field//27  # thick_row - block of rows
			tcol = field%9//3  # thick_col - block of collumns
			box = [self.grid[trow*27+tcol*3+x+y*9] for y in range(3) for x in range(3)]

			possibilities = [x for x in range(0+1,9+1) if x not in row and x not in col and x not in box]
			shuffle(possibilities)

			# print(possibilities)
			for current_choice in possibilities:
				self.grid[field] = current_choice

				if field == 80:
					self.grid[field] = 0
					return True

				if self.solve_grid(field+1):
					self.grid[field] = 0
					return True

			# backtrace
			self.grid[field] = 0
			return False

		elif field == 80:
			return True
		else:
			return self.solve_grid(field+1)

	def prepare_grid(self, difficulty='medium'):
		ready = False
		attempt = 1
		while not ready:
			base_grid = [x for x in self.grid]
			print('attempt: ', attempt)
			ready = self.remove_values(difficulty)
			if not ready:
				self.grid = [x for x in base_grid]
				attempt += 1

	def remove_values(self, difficulty):
		quantities = {1:9, 2:9, 3:9, 4:9, 5:9, 6:9, 7:9, 8:9, 9:9}
		emptied = False
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
		# 	forbiden_digits = set(grid[i] for i in row+col+box)
		# 	options[x] = [n for n in range(1, 9+1) if n not in forbiden_digits]
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



		# row = self.grid[field-field%9 : field//9*9+9]
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
		options = {x:list(range(1, 9+1)) for x in range(81) if not grid[x]}
		field_relations = {}
		solved_fields = []
		# for every empty field (containing 0)
		for field in options:
			# calculating related indexes
			row = list(range(field-field%9, field//9*9+9))
			col = [x*9+field%9 for x in range(9)]
			box = [field//27*27+field%9//3*3+a+b*9 for b in range(3) for a in range(3)]
			related_indexes = list( set(row + col + box) )

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
		box_ids = [[(27*ver+3*hor)//27*27+(27*ver+3*hor)%9//3*3+a+b*9 for b in range(3) for a in range(3)] for hor in range(3) for ver in range(3)]

		while 0 in grid:
			options_ref = deepcopy(options)

			# infering in every box
			for box in box_ids:
				self.infer_in_box(options, box_ids, box)

			for field in options.keys():
				if not len(options[field]):
					print('bledne rozwiazanie, brak opcji dla pola', field)
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

