#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import random
from itertools import zip_longest

CELL_SIZE = 100 # in pixels
GRID_LEN = 4
GRID_PADDING = 10

BACKGROUND_COLOR_GAME = "#92877d"
BACKGROUND_COLOR_DICT = {   '2':"#eee4da",'4':"#ede0c8", '8':"#f2b179", '16':"#f59563",
                            '32':"#f67c5f", '64':"#f65e3b", '128':"#edcf72", '256':"#edcc61",
                            '512':"#edc850", '1024':"#edc53f", '2048':"#edc22e", None: "#9e948a"}
CELL_COLOR_DICT = { '2':"#776e65", '4':"#776e65", '8':"#f9f6f2", '16':"#f9f6f2", # foregrounds
                    '32':"#f9f6f2", '64':"#f9f6f2", '128':"#f9f6f2", '256':"#f9f6f2",
                    '512':"#f9f6f2", '1024':"#f9f6f2", '2048':"#f9f6f2" }

BACKGROUND_COLOR_DICT = {   2:"#eee4da", 4:"#ede0c8", 8:"#f2b179", 16:"#f59563",
                            32:"#f67c5f", 64:"#f65e3b", 128:"#edcf72", 256:"#edcc61",
                            512:"#edc850", 1024:"#edc53f", 2048:"#edc22e", None: "#9e948a" }
CELL_COLOR_DICT = { 2:"#776e65", 4:"#776e65", 8:"#f9f6f2", 16:"#f9f6f2",
                    32:"#f9f6f2", 64:"#f9f6f2", 128:"#f9f6f2", 256:"#f9f6f2",
                    512:"#f9f6f2", 1024:"#f9f6f2", 2048:"#f9f6f2" , None: "#9e948a"}

FONT = ("Verdana", 40, "bold")

class Cell(tk.Label):
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, justify=tk.CENTER, font=FONT, **kwargs)
        self.value = None
        self.change()

    def change(self, value=None):
        text = str(value) if value is not None else ''
        self.config(text=text, bg=BACKGROUND_COLOR_DICT[value], fg=CELL_COLOR_DICT[value])
        self.value = value

class Message(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, bd=4, relief=tk.RIDGE, **kwargs)
        self.lbl = tk.Label(self, font=FONT)
        self.lbl.pack()

        btn = tk.Button(self, font=FONT, text='Restart', command=master.restart)
        btn.pack()

    def show(self, text):
        self.lbl.config(text=text)
        self.tkraise()

class GameGrid(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, bg=BACKGROUND_COLOR_GAME, **kwargs)

        master.cells = [Cell(self) for _ in range(GRID_LEN**2)]
        for idx, cell in enumerate(master.cells):
            row, col = divmod(idx, GRID_LEN)
            cell.grid(row=row, column=col, padx=GRID_PADDING, pady=GRID_PADDING, sticky='nsew')

        for i in range(GRID_LEN):
            self.rowconfigure(i, minsize=CELL_SIZE)
            self.columnconfigure(i, minsize=CELL_SIZE)

def compute(row):
    '''computes the row to the left'''
    row = filter(None, row)
    state = None
    output = []
    for element in row:
        if element == state:
            output.append(element * 2)
            state = None
        elif state is None:
            state = element
        else:
            output.append(state)
            state = element
    if state is not None:
        output.append(state)
    return output

class Game(tk.Tk):
    def __init__(self, **kwargs):
        tk.Tk.__init__(self, **kwargs)
        self.title('2048')
        for key in ('<Up>', '<Down>', '<Left>', '<Right>'):
            self.bind(key, self.keypress)

        self.message = Message(self)
        self.message.place(relx=.5, rely=.5, anchor=tk.CENTER)

        self.grid = GameGrid(self)
        self.grid.pack()

        self.restart()

    def restart(self):
        self.running = True
        self.grid.tkraise()
        for cell in self.cells:
            cell.change()
        self.drop_a_two()
        self.drop_a_two()

    def keypress(self, event=None):
        if not self.running:
            return
        if event.keysym == 'Left':
            self.shift(self.get_rows())
        elif event.keysym == 'Up':
            self.shift(list(self.get_cols()))
        elif event.keysym == 'Right':
            self.shift(self.get_rows(), True)
        elif event.keysym == 'Down':
            self.shift(list(self.get_cols()), True)

    def shift(self, rows, reverse=False):
        new_rows = []
        changed = False
        for row in rows:
            values = [cell.value for cell in row]
            new_values = compute(reversed(values) if reverse else values)
            if reverse and values[-len(new_values):] != new_values[::-1]:
                changed = True
            if not reverse and values[:len(new_values)] != new_values:
                changed = True
            new_rows.append(new_values)

        if not changed:
            return # move is illegal as there is nothing to do
        for new_values, row in zip(new_rows, rows):
            for cell, new_value in zip_longest(reversed(row) if reverse else row, new_values):
                cell.change(new_value)

        # check for winners
        if 64 in [cell.value for cell in self.cells]:
            self.message.show('You Win!!')
            self.running = False

        self.drop_a_two()

        # check for losers
        if not self.moves_available():
            self.message.show('You Lose!!')
            self.running = False

    def drop_a_two(self):
        '''randomly pick an empty cell and make it a 2'''
        empty_cells = [cell for cell in self.cells if cell.value is None]
        random.choice(empty_cells).change(2)

    def moves_available(self):
        '''check if there are any moves left'''
        for row in self.get_rows():
            values = [cell.value for cell in row]
            if compute(values) != values:
                return True
        for row in self.get_cols():
            values = [cell.value for cell in row]
            if compute(values) != values:
                return True
        return False

    def get_rows(self):
        return [self.cells[i:i+GRID_LEN] for i in range(0, GRID_LEN**2, GRID_LEN)]

    def get_cols(self):
        return zip(*self.get_rows())

r = Game()
r.mainloop()
