from tkinter import *
from enum import Enum
import os
import numpy as np

cwd = os.getcwd()


class Game_state(Enum):
    MENU = 0
    STARTUP = 1
    GAME = 2
    DONE = 3


DIF = 2  # 0 = Easy, 1 = Intermediate, 2 = Hard
ROWS = [9, 16, 16]
COLS = [9, 16, 30]
MINES = [9, 40, 99]

ROW = ROWS[DIF]
COL = COLS[DIF]
MINE = MINES[DIF]
SIZE = ROW*COL


class Minesweeper():

    def __init__(self):

        # Initial Game State
        self.game_state = Game_state.STARTUP

        self.start_game()

    def __convert(self, index=None, x=0, y=0):
        if not (index is None):
            return index % COL, int(index/COL)
        else:
            return y*COL + x

    def start_game(self):

        # Random initial move
        initial_move = np.random.randint(SIZE)

        # Generate tile arrays
        self.tiles = np.zeros(SIZE)
        self.seen_tiles = np.zeros((ROW+4, COL+4))

        # Place mines
        possible_mine_placement = [i for i in range(SIZE) if i != initial_move]
        mine_indexes = np.random.choice(
            possible_mine_placement, size=MINE, replace=False)
        self.tiles[mine_indexes] = -1

        # Calculate numbers surrounding mines
        self.tiles = np.reshape(self.tiles, (ROW, COL))
        mine_pos = np.copy(self.tiles)

        # Stores bomb_pos in each of the 8 offset positions creating a superposition of all bomb-positions
        mine_counter = np.zeros(((ROW+2), (COL+2)))
        for x, y in ((0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)):
            mine_counter[x:x+ROW, y:y+COL] += mine_pos

        # Remove mine padding, and set bomb_locations to 0
        mine_counter = mine_counter[1:-1, 1:-1]
        mine_counter[np.where(mine_pos == -1)] = 0
        self.tiles += np.abs(mine_counter)

        # Add padding to tiles
        tiles = np.zeros((ROW+4, COL+4))
        tiles[2:2+ROW, 2:2+COL] = self.tiles
        self.tiles = tiles

        self.open_tile(initial_move)

    def open_tile(self, move):

        # Get move as x,y position
        x, y = self.__convert(index=move)

        self.seen_tiles[x+2, y+2] = self.tiles[x+2, y+2]

        pt = self.get_surrounding_tiles(x+2, y+2)

        while len(pt) > 0:

            print(pt[0])

    def get_surrounding_tiles(self, x, y):
        points = []
        for i, j in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            dx, dy = x+i, y+j
            if (0 <= dx < ROW) and (0 <= dy < COL):
                points.append(self.__convert(x=dy, y=dx))
        return np.array(points)

    def print_game(self, ls=None):
        signs = [' ', '1', '2', '3', '4', '5', '6', '7', '8', '\u2605']

        if ls is None:
            r = ROW
            c = COL
            ls = self.tiles
        else:
            r = np.shape(ls)[0]
            c = np.shape(ls)[1]

        for i in range(r):
            for j in range(c):
                print(signs[int(ls[i, j])], end=' ')
            print()

    # Generate Data

    def generate_data(self, event, num=1):

        x = np.random.randint(0, COL, num)
        y = np.random.randint(0, ROW, num)

        for i in range(num):
            self.new_game()

            index = self.tile_index(x[i], y[i])
            self.generate_board(
                row=ROW, col=COL, bomb=self.setting('bomb'), initial=index)
            self.game_state = Game_state.GAME
            self.tile_action(i=index, action='open')

            tile_list = self.detect_openable_tiles()
            # For item in list run network - also remember to optimize list in code!

    def detect_openable_tiles(self):

        ls = []

        row = self.setting('row')
        col = self.setting('col')

        b = np.reshape(self.seen_tiles,
                       (self.setting('row'), self.setting('col')))
        a = np.where(b != np.inf)

        for i in range(len(a[0])):
            for x, y in ((0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)):
                ls.append([a[0][i]+x, a[1][i]+y])

        for i, pair in enumerate(ls):
            if (pair[0] < 0 or pair[0] > row):
                ls.pop[i]
            if (pair[1] < 0 or pair[1] > col):
                ls.pop[i]
        return ls


game_instance = Minesweeper()
