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
            

    def mainloop(self):
        self.window.mainloop()


game_instance = Minesweeper()
game_instance.mainloop()