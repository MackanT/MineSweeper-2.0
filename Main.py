from tkinter import *
from enum import Enum
import os
import csv
# import threading
import numpy as np
import time

cwd = os.getcwd()

class Game_state(Enum):
    MENU = 0
    GAME = 1
    DEBUG = 2
    BOT = 3

class Minesweeper():
    
    def __init__(self):
        
        ### Initial Game State
        self.game_state = Game_state.MENU

        # Load Application Data              

        self.dif = 'hard'
        self.game_parameters = self.__load_settings('settings')

        # Screen Settings
        self.window = Tk()
        self.window.title('The Electric Boogaloo - Minesweeper 2')
        self.window.config(bg=self.__setting('menu_color', 0))
        self.canvas = Canvas(self.window, 
                             width = self.__setting('size', 0), 
                             height = self.__setting('size', 1), 
                             bg=self.__setting('menu_color', 0),
                             borderwidth=0,
                             highlightthickness=0
                            )
        self.canvas_board = Canvas(self.window, 
                             width = 0, 
                             height = 0, 
                             highlightthickness=1
                            )

        ### TODO add menu creating below

        self.canvas_board.bind('<Button-1>', self.left_click)
        self.canvas_board.bind('<Button-3>', self.right_click)

        self.window.resizable(False, False)
        self.canvas.pack()

        self.draw_game(col=self.setting('col'), row=self.setting('row'))
        # self.test_code()

    def test_code(self):
        in_time = time.time()
        for i in range(1000):
            self.draw_game(row=16, col=30, bomb=99)
        print('Time ellapsed: {} s'.format(time.time()-in_time))

    ### Game Logic / Behing the scenes

    def __get_font(self, size=20, bold=True):
        if bold: return ("GOST Common", size, "bold")
        else: return ("GOST Common", size)   

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

    def setting(self, name):
        
        if name == 'col':
            return self.__setting(self.dif, 0)
        elif name == 'row':
            return self.__setting(self.dif, 1)
        elif name == 'w':
            return self.__setting('size', 2) 
        elif name == 'bomb':
            return self.__setting(self.dif, 2)
    
    ### User Input

    def __click_to_tile(self, event):
        w = self.setting('w')
        x = int(event.x/w)
        y = int(event.y/w)
        return x, y

    def left_click(self, event):

        x, y = self.__click_to_tile(event)

        if self.game_state == Game_state.MENU:

            index = self.tile_index(x, y)
            row = self.setting('row')
            col = self.setting('col')

            self.generate_board(row=row, col=col, bomb=self.setting('bomb'), initial=index)
            self.game_state = Game_state.DEBUG
        
        self.tile_action(x=x, y=y, action='open')
       
    def right_click(self, event):
        x, y = self.__click_to_tile(event)
        self.tile_action(x=x, y=y, action='flag')
    
    def tile_action(self, x=0, y=0, action='open'):
        
        i = self.tile_index(x, y)

        if action == 'open':
            if not self.__is_flagged(i):
                self.update_tiles(points=i, state='open')
            
        elif action == 'flag':
            if self.__is_open(i): return
            if self.__is_flagged(i):
                self.update_tiles(points=i, state='hidden')
            elif not self.__is_flagged(i):
                self.update_tiles(points=i, state='flag')

        self.window.update()

    def tile_index(self, x, y):
        return x + y*self.setting('col')
    
    def tile_xy(self, index):
        x = int(index / self.setting('col'))
        y = index % self.setting('col')
        return x, y

    def __is_open(self, i):
        return 0 < self.seen_tiles[i] < np.inf

    def __is_flagged(self, i):
        return self.seen_tiles[i] == -np.inf

    ### Initialize Game

    def draw_game(self, row=16, col=30):

        w = self.setting('w')
        self.canvas_board.configure(state='normal',
                        width=col*w,
                        height=row*w,
                        )
        self.canvas.config(
                        width=(col+2)*w,
                        height=(row+2)*w,
                        )
        self.window.geometry('%dx%d'%((col+2)*w, (row+2)*w))
        self.canvas_board.place(x=w, y=w, anchor=NW)
        self.draw_tiles(row=row, col=col, w=w)

    def generate_board(self, row, col, bomb, initial):

        game_size = row*col

        tile_indexes = [i for i in range(game_size) if i != initial]
        bomb_indexes = np.random.choice(tile_indexes, size=bomb, replace=False)
        
        self.tile_values = np.zeros(game_size)
        self.tile_values[bomb_indexes] = -1
        self.tile_values = np.reshape(self.tile_values, (col, row))

        bomb_pos = np.copy(self.tile_values)
        bomb_counter = np.zeros(((col+2),(row+2)))

        for x, y in ((0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)):
            bomb_counter[x:x+col,y:y+row] += bomb_pos

        ### Remove earlier added padding, and set bomb_locations to 0
        bomb_counter = bomb_counter[1:-1,1:-1]
        bomb_counter[np.where(bomb_pos == -1)] = 0
        self.tile_values += np.abs(bomb_counter)
        self.tile_values = np.reshape(self.tile_values.T, game_size)
        self.draw_numbers(row=row, col=col)

        # for i in range(col):
        #     for j in range(row):
        #         index = i + j*col
        #         self.canvas_board.itemconfig(self.drawn_tiles_num[index], state='normal')
        

    def draw_tiles(self, row, col, w):

        self.drawn_tiles = np.zeros(col*row, dtype=object)
        self.drawn_tiles_num = np.zeros(col*row, dtype=object)
        self.seen_tiles = np.ones(col*row)*np.inf
        color = self.__setting('tile_color', 0)
        column = self.setting('col')

        for i in range(col):
            for j in range(row):
                index = i + j*column
                self.drawn_tiles[index] = (
                        self.canvas_board.create_rectangle(i*w, j*w, 
                                                          (i+1)*w, (j+1)*w, 
                                                          fill=color))
                self.drawn_tiles_num[index] = (
                        self.canvas_board.create_text((i+.5)*w, (j+.5)*w, 
                        text='', font=self.__get_font(size=int(w/2))))

    def draw_numbers(self, row, col):
        column = self.setting('col')
        w = self.setting('w')

        for i in range(col):
            for j in range(row):
                index = i + j*column
                text = self.tile_values[index]
                color = self.__setting('tile_color_num', int(text))
                text = '' if (text == 0 or text == -1) else int(text)
                self.drawn_tiles_num[index] = (
                        self.canvas_board.create_text((i+.5)*w, (j+.5)*w, 
                        text='{}'.format(text), 
                        font=self.__get_font(size=int(w/2)),
                        fill=color, state='hidden'))

    def update_tiles(self, points, state='hidden'):

        if type(points) == int: points = [points]

        if state == 'hidden':
            color = self.__setting('tile_color', 0)
            self.seen_tiles[points] = np.inf
            for p in points:
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)
        
        elif state == 'open':

            self.window.update()
            text = self.tile_values[points]
            self.seen_tiles[points] = text

            ### Open all input bombs - will never really happen as only 1 bomb can normally be opened at a time.... ;-)
            if -1 in text:
                n_list = []
                for i, p in enumerate(text):
                    if p != -1: continue
                    n_list.append(points[i])
                self.update_tiles(n_list, 'bomb')
                return
            
            n_list = []
            color = self.__setting('tile_color', 1)
            for i, p in enumerate(points):
                
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)
                self.canvas_board.itemconfig(self.drawn_tiles_num[p], state='normal')

                if self.seen_tiles[p] == 0:
                    sur_tiles = self.get_surrounding_tiles(points[i])                                
                    for d in sur_tiles:
                        if self.seen_tiles[d] == np.inf and d not in n_list:
                            n_list.append(d)
            if len(n_list) > 0:
                self.update_tiles(n_list, 'open')
                return

            

            # for p in points:
                # if p == -5: continue
                

        elif state == 'flag':
            ### TODO update flag counter
            self.seen_tiles[points] = -np.inf
            color = self.__setting('tile_color', 2)
            for p in points:
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)

        elif state == 'bomb':
            ### TODO add game over code!
            color = self.__setting('tile_color', 3)
            # self.seen_tiles[points] = -1
            for p in points:
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)
            print('Game Over')
    
    def get_surrounding_tiles(self, index):
        
        i, j = self.tile_xy(index)
        col = self.setting('col')
        row = self.setting('row')
        points = []

        for x, y in ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)):
            dx, dy = i+x, j+y
            if (0 <= dx < row) and (0 <= dy < col):
                points.append(self.tile_index(dy, dx))
        return points

    def mainloop(self):
        self.window.mainloop()


game_instance = Minesweeper()
game_instance.mainloop()