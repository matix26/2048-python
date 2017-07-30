#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import random
from itertools import zip_longest

CELL_SIZE = 100 # in pixels
GRID_LEN = 4
GRID_PADDING = 10

BACKGROUND_COLOR_GAME = "#92877d"

COLORS = {
    # (foreground color, background color)
    2:    ("#776e65", "#eee4da"),
    4:    ("#776e65", "#ede0c8"),
    8:    ("#f9f6f2", "#f2b179"),
    16:   ("#f9f6f2", "#f59563"),
    32:   ("#f9f6f2", "#f67c5f"),
    64:   ("#f9f6f2", "#f65e3b"),
    128:  ("#f9f6f2", "#edcf72"),
    256:  ("#f9f6f2", "#edcc61"),
    512:  ("#f9f6f2", "#edc850"),
    1024: ("#f9f6f2", "#edc53f"),
    2048: ("#f9f6f2", "#edc22e"),
    None: ("#9e948a", "#9e948a"),
    }

WINNER = 2048
WINNER = 16
FONT = ("Verdana", 40, "bold")
FONT_MED = ("Verdana", 25, "bold")
FONT_SMALL = ("Verdana", 18, "bold")

class Cell(tk.Label):
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, justify=tk.CENTER, font=FONT, **kwargs)
        self.value = None
        self.change()

    def change(self, value=None):
        self.value = value
        text = str(value) if value is not None else ''
        if value is not None:
            while value > WINNER:
                value //= WINNER
        fg, bg = COLORS[value]
        self.config(text=text, bg=bg, fg=fg)

class LoseMessage(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, bd=4, relief=tk.RIDGE, **kwargs)
        self.lbl = tk.Label(self, text="You Lose!!", font=FONT)
        self.lbl.pack()

        btn = tk.Button(self, font=FONT, text='Restart', command=master.restart)
        btn.pack()

class WinMessage(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, bd=4, relief=tk.RIDGE, **kwargs)
        self.lbl = tk.Label(self, text="You Win!!", font=FONT)
        self.lbl.pack()

        btn = tk.Button(self, font=FONT, text='Continue', command=self.cont)
        btn.pack(fill=tk.X, expand=True)

        btn = tk.Button(self, font=FONT, text='Restart', command=master.restart)
        btn.pack(fill=tk.X, expand=True)

    def cont(self):
        self.master.mode = 'overtime'
        self.master.grid.tkraise()

class GameGrid(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, bg=BACKGROUND_COLOR_GAME, **kwargs)

        master.cells = [Cell(self) for _ in range(GRID_LEN**2)]
        for idx, cell in enumerate(master.cells):
            row, col = divmod(idx, GRID_LEN)
            cell.grid(row=row, column=col, padx=GRID_PADDING, pady=GRID_PADDING, sticky='nsew')

        for i in range(GRID_LEN):
            self.rowconfigure(i, minsize=CELL_SIZE, weight=1)
            self.columnconfigure(i, minsize=CELL_SIZE, weight=1)

def compute(row):
    '''computes the row towards the left'''
    row = filter(None, row)
    state = None
    output = []
    score = 0
    for element in row:
        if element == state:
            output.append(element * 2)
            score += element * 2
            state = None
        elif state is None:
            state = element
        else:
            output.append(state)
            state = element
    if state is not None:
        output.append(state)
    return output, score

class ScoreBox(tk.Frame):
    def __init__(self, master=None, name=None, **kwargs):
        tk.Frame.__init__(self, master, bg=BACKGROUND_COLOR_GAME, width=CELL_SIZE, height=CELL_SIZE, **kwargs)
        self.pack_propagate(False)
        lbl = tk.Label(self, text=name, font=FONT_SMALL, bg=BACKGROUND_COLOR_GAME, fg='white')
        lbl.pack()

        var = tk.IntVar()
        lbl = tk.Label(self, textvariable=var, font=FONT_MED, bg=BACKGROUND_COLOR_GAME, fg='white')
        lbl.pack(fill=tk.Y, expand=True)
        self.set, self.get = var.set, var.get

class Status(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        btn = tk.Button(self, text='New\nGame', font=FONT_SMALL, command=master.restart)
        btn.pack(side=tk.LEFT)
        self.high_score = ScoreBox(self, "BEST")
        self.high_score.pack(side=tk.RIGHT, padx=GRID_PADDING, pady=GRID_PADDING)
        self.curr_score = ScoreBox(self, "SCORE")
        self.curr_score.pack(side=tk.RIGHT, padx=GRID_PADDING, pady=GRID_PADDING)

        try:
            with open('high_score') as f:
                self.high_score.set(int(f.read()))
        except IOError:
            pass

    def inc_score(self, score):
        self.curr_score.set(self.curr_score.get() + score)
        if self.curr_score.get() > self.high_score.get():
            self.high_score.set(self.curr_score.get())
            with open('high_score', 'w') as f:
                f.write(str(self.curr_score.get()))

class Game(tk.Tk):
    def __init__(self, **kwargs):
        tk.Tk.__init__(self, **kwargs)
        self.title('2048')
        for key in ('<Up>', '<Down>', '<Left>', '<Right>'):
            self.bind(key, self.keypress)

        self.status = Status(self)
        self.status.pack(fill=tk.X)

        self.winmessage = WinMessage(self)
        self.winmessage.place(relx=.5, rely=.5, anchor=tk.CENTER)

        self.losemessage = LoseMessage(self)
        self.losemessage.place(relx=.5, rely=.5, anchor=tk.CENTER)

        self.grid = GameGrid(self)
        self.grid.pack(fill=tk.BOTH, expand=True)

        self.restart()

    def restart(self):
        self.mode = 'normal' # can be 'lost', 'won', 'overtime'
        self.status.curr_score.set(0)
        self.grid.tkraise()
        for cell in self.cells:
            cell.change()
        self.drop_a_two()
        self.drop_a_two()

    def keypress(self, event=None):
        if self.mode in ('lost', 'won'):
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
        score = 0
        for row in rows:
            values = [cell.value for cell in row]
            new_values, s = compute(reversed(values) if reverse else values)
            score += s
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

        self.status.inc_score(score)

        # check for winners
        if self.mode == 'normal' and WINNER in [cell.value for cell in self.cells]:
            self.mode = 'won'
            self.winmessage.tkraise()

        self.drop_a_two()

        # check for losers
        if not self.moves_available():
            self.mode = 'lost'
            self.losemessage.tkraise()

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
