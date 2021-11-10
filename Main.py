from tkinter import *
from enum import Enum
# from PIL import Image, ImageTk
import os
import csv
import threading
import numpy as np

cwd = os.getcwd()

class Game_state(Enum):
    GAME = 0
    DEBUG = 1
    BOT = 2

class Minesweeper():
    
    def __init__(self):
        
        ### Initial Game State
        self.game_state = Game_state.DEBUG

        # Load Application Data              
        self.game_parameters = self.__load_settings('settings')

        # Screen Settings
        self.window = Tk()
        self.window.title('The Electric Boogaloo - Minesweeper 2')
        self.window.config(bg=self.__setting('menu_color', 0))
        self.canvas = Canvas(self.window, 
                             width = self.__setting('screen_size', 0), 
                             height = self.__setting('screen_size', 1), 
                             bg=self.__setting('menu_color', 0),
                             borderwidth=0,
                             highlightthickness=0
                            )
        self.game_canvas = Canvas(self.window, 
                             width = 0, 
                             height = 0, 
                             highlightthickness=1
                            )
        self.test_canvas = []
        self.window.resizable(False, False)
        self.canvas.pack()

    def __setting(self, name, index):
        """ returns setting 'name' with position 'index' """
        for row in self.game_parameters:
            if row[0] == name: return row[1][index]
        return False

    def __load_settings(self, folder):
        """ returns list of lists with loaded settings. Loaded file: cwd\\folder.csv """
        
        file_name = cwd + '\\{}.csv'.format(folder)

        if self.game_state == Game_state.DEBUG:
            print('Loading settings in folder: {}'.format(file_name))

        ### TODO Add crash/try something if file does not exist!        
        if not os.path.exists(file_name): 
            print('File {} does not exist!'.format(file_name))
            return False

        with open(file_name) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')
            next(csv_reader)
            data = []
            for row in csv_reader:
                data_length = int(row[1])
                data_type = row[2]
                tmp = [row[0], row[3:3+data_length]]
                if data_type == 'int':
                    tmp[1][:] = (int(tmp[1][i]) for i in range(len(tmp[1])))
                data.append(tmp)
        return data
            
    def start_game(self, row=16, col=30, bomb=99, initial=0):
        self.generate_board(row=row, col=col, bomb=bomb, initial=initial)
        self.draw_board(row=row, col=col)


    def generate_board(self, row, col, bomb, initial):

        game_size = row*col

        tile_indexes = [i for i in range(game_size) if i != initial]
        bomb_indexes = np.random.choice(tile_indexes, size=bomb, replace=False)
        
        self.tile_values = np.zeros(game_size)
        self.tile_values[bomb_indexes] = -1

        bomb_pos = np.copy(self.tile_values)
        bomb_pos = np.reshape(bomb_pos, (row, col))
        bomb_counter = np.zeros(((row+2),(col+2)))

        for x, y in ((0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)):
            bomb_counter[x:x+row,y:y+col] += bomb_pos

        ### Remove earlier added padding, and set bomb_locations to 0
        bomb_counter = bomb_counter[1:-1,1:-1]
        bomb_counter[np.where(bomb_pos == -1)] = 0
        self.tile_values += np.reshape(np.abs(bomb_counter), game_size)        

    def draw_board(self, row, col):

        self.drawn_tiles = np.zeros((row, col), dtype=object)
        self.drawn_tiles_num = np.zeros((row, col), dtype=object)
        tmp = np.reshape(self.tile_values, (row, col))
        w = 60

        for i in range(row):
            for j in range(col):
                self.drawn_tiles[i,j] = self.canvas.create_rectangle(i*w, j*w, (i+1)*w, (j+1)*w, fill='#ffffff')
                self.drawn_tiles_num[i,j] = self.canvas.create_text((i+.5)*w, (j+.5)*w, fill='#000000', text=tmp[i,j])
                if tmp[i,j] == -1:
                    self.canvas.itemconfig(self.drawn_tiles[i,j], fill='#3ee121')


    def print_board(self, x, y):
        print(np.reshape(self.tile_values, (x, y)))


    def mainloop(self):
        self.window.mainloop()


game_instance = Minesweeper()
game_instance.mainloop()