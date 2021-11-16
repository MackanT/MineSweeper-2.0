from tkinter import *
from enum import Enum
import os
import csv
import threading
import numpy as np
import time

cwd = os.getcwd()

class Game_state(Enum):
    MENU = 0
    STARTUP = 1
    GAME = 2
    DONE = 3
    DEBUG = 4
    BOT = 5


class Minesweeper():
    
    def __init__(self):
        
        ### Initial Game State
        self.game_state = Game_state.STARTUP

        # Load Application Data              

        self.dif = 'hard'
        self.game_parameters = self.__load_settings('settings')
        self.array_button = []

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
                             highlightthickness=2,
                             highlightcolor=self.__setting('menu_color', 3)
                            )

        ### TODO add menu creating below

        self.canvas.bind('<Button-1>', self.button_click)
        self.canvas_board.bind('<Button-1>', self.left_click)
        self.canvas_board.bind('<Button-2>', self.middle_click)
        self.canvas_board.bind('<Button-3>', self.right_click)
        self.canvas_board.bind('<space>', self.middle_click)
        self.canvas_board.bind('<e>', self.initiate_bot)
        self.canvas_board.focus_set()

        self.window.resizable(False, False)
        self.canvas.pack()

        self.draw_game(col=self.setting('col'), row=self.setting('row'))

        self.start_timer()

        # self.test_code()

    def test_code(self):
        in_time = time.time()
        for i in range(1000):
            self.draw_game(row=16, col=30, bomb=99)
        print('Time ellapsed: {} s'.format(time.time()-in_time))

    ### Timer Functions

    def start_timer(self):
        threading.Timer(1.0, self.start_timer).start()
        if self.game_state == Game_state.GAME:
            self.game_time += 1
            self.__update_timer()


    ### Game Logic / Behing the scenes

    def __get_font(self, size=20, bold=True):
        if bold: return ("GOST Common", size, "bold")
        else: return ("GOST Common", size)   

    def __setting(self, name, index):
        """ returns setting 'name' with position 'index' """
        for row in self.game_parameters:
            if row[0] == name: 
                if index == -1: return row[1]
                return row[1][index]
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

        with open(file_name, encoding="utf-8") as csvfile:
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
    
    ### BOT

    def initiate_bot(self, event):
        """ Initiates minesweeper auto-solver, ensures it can only run once/game """

        if self.game_state != Game_state.BOT:
            self.game_state = Game_state.BOT
            self.run_bot(initial_run=True)

    def run_bot(self, initial_run=False):

        if self.game_state != Game_state.BOT: return
        
        if initial_run:

            game_size = np.size(self.seen_tiles)
            bombs = self.setting('bomb')
            row = self.setting('row')
            col = self.setting('col')

            self.completed_tiles = np.zeros(game_size, bool)

            open_tile = np.random.choice(range(game_size), 1)[0]

            self.generate_board(row=row, col=col, bomb=bombs, initial=open_tile)
            self.tile_action(open_tile)
        else:
            print('Backtracking!')

        while True:
            if self.check_tiles() == False: break

        print('No more basic moves - Starting up backtracking')

        self.window.update()
        if self.backtrack_bot():
            self.run_bot()

        if self.game_state != Game_state.BOT: return
        open_tile = self.get_random_tile()
        print('Opening ', open_tile)
        self.update_tiles(open_tile, state='open')
        self.run_bot()

    def get_random_tile(self):
        hidden_index = np.where(self.seen_tiles == np.inf)[0]
        return np.random.choice(hidden_index, 1)[0]

    def get_interesting_tiles(self):

        t_hidden = np.where(self.seen_tiles != np.inf)[0]
        t_blank = np.where(self.seen_tiles != 0)[0]
        t_done = np.where(self.completed_tiles == False)[0]
        tile_check = np.intersect1d(t_hidden, t_blank)
        return np.intersect1d(tile_check, t_done)

    def logic_search(self, chain, tile, board, neig):
        
        tile_check = self.get_surrounding_tiles(tile)
        hidden_index = np.where(board[tile_check] == np.inf)[0]
        n_hidden = tile_check[hidden_index]

        tmp = self.get_surrounding_tiles(neig)
        t_index = np.where(board[tmp] == np.inf)[0]
        t_hidden = tmp[t_index]

        a = np.setxor1d(n_hidden, t_hidden)
        
        if len(a) == 0: return False

        f_index = np.where(board[tmp] == -np.inf)[0]

        if len(a) > board[neig]: return False
        if len(f_index) + 1 == board[neig]:
            self.update_tiles(a, state='open')
            return True
        elif len(f_index) + len(a) + 1 == board[neig]:
            self.update_tiles(a, state='flag')
            return True
        return False

    def get_chain(self, tile, board, chain):

        nearby_tiles = self.get_surrounding_tiles(tile)
        a = board[nearby_tiles]
        num_index = np.where(np.logical_and(a>=1, a<=8))
        nearby_tiles = nearby_tiles[num_index]
        for t in nearby_tiles:
            if t not in chain:
                chain.append(t)
                self.get_chain(t, board, chain)
        return chain

    def backtrack_bot(self):
        
        logic_success = False
        tile_check = self.get_interesting_tiles()
        temp_board = np.zeros(np.size(self.seen_tiles))
        temp_board[tile_check] = self.seen_tiles[tile_check]

        chains = []
        for tile in tile_check:
            chain = [tile]
            if len(chains) == 0:
                chains.append(self.get_chain(tile=tile, board=temp_board, chain=chain))
            else:
                if any(tile in i for i in chains): continue
                chains.append(self.get_chain(tile=tile, board=temp_board, chain=chain))
        
        # Gathers neighbouring values to interesting tiles
        for tile in tile_check:
            nearby_tiles = self.get_surrounding_tiles(tile)
            temp_board[nearby_tiles] = self.seen_tiles[nearby_tiles]

        for c in chains:
            if len(c) == 1: continue
            ### TODO add logic to jump chain if all have been attempted, i.e. chain [1, 17] is done if not found for 1

            ### TODO optimize so attempts every chain and possible several attempts / Chain before returning
            for tile in c: 

                nearby_tiles = self.get_surrounding_tiles(tile)
                n_index = np.where(temp_board[nearby_tiles] == np.inf)[0]
                
                if len(n_index) <= temp_board[tile] - 1: continue

                n_tiles = nearby_tiles[n_index]
                flag_index = np.where(temp_board[nearby_tiles] == -np.inf)[0]
                flag_rem = temp_board[tile] - len(flag_index)

                ### Start with easiest case, i.e. only 2 options
                if flag_rem != 1: continue
    
                for neig in np.intersect1d(nearby_tiles, c):

                    n = self.get_surrounding_tiles(neig)
                    n_ind = np.where(temp_board[n] == np.inf)[0]
                    n = n[n_ind]
                    
                    if sum(np.isin(n, n_tiles)) == 2:
                        if self.logic_search(chain=c, tile=tile, board=temp_board, neig=neig):
                            logic_success = True
                            self.window.update()
                            self.run_bot()
                            tmp = self.get_interesting_tiles()
                            temp_board[tmp] = self.seen_tiles[tmp]
                        break
                
        return logic_success
                
    def check_tiles(self):

        operation_done = False
        tile_check = self.get_interesting_tiles()

        for tile in tile_check:

            # print('Checking tile#: {}'.format(tile))
            
            tile_num = self.tile_values[tile]
            nearby_tiles = self.get_surrounding_tiles(tile)

            hidden_index = np.where(self.seen_tiles[nearby_tiles] == np.inf)[0]
            flag_index = np.where(self.seen_tiles[nearby_tiles] == -np.inf)[0]
            
            if np.size(flag_index) == tile_num:
                self.update_tiles(nearby_tiles[hidden_index], state='open')
                self.completed_tiles[tile] = True
                operation_done = True
            elif np.size(hidden_index) + np.size(flag_index) == tile_num:
                self.update_tiles(nearby_tiles[hidden_index], state='flag')
                self.completed_tiles[tile] = True
                operation_done = True
                
        return operation_done

    ### User Input

    def __click_to_tile(self, event):
        w = self.setting('w')
        x = int(event.x/w)
        y = int(event.y/w)
        return x, y

    def find_clicked_button(self, x, y):
        for i, item in enumerate(self.array_button): 
            if item.point_in_box(x, y):
                return self.array_button[i].get_name()

    def button_click(self, event):
            
        button_clicked = self.find_clicked_button(event.x, event.y)
        if button_clicked == None: return
        button_names = self.__setting('buttons', -1)

        if button_clicked == button_names[0]:
            self.menu_difficulty_select()
        elif button_clicked == button_names[1]:
            self.menu_statistics()
        elif button_clicked == button_names[2]:
            self.menu_settings()
        elif button_clicked == button_names[3]: 
            self.menu_credits()
        elif button_clicked == button_names[4]:
            self.window.destroy()
        elif button_clicked == button_names[5]:
            self.leave_startup(0)
        elif button_clicked == button_names[6]:
            self.leave_startup(1)
        elif button_clicked == button_names[7]:
            self.leave_startup(2)
        elif button_clicked == button_names[8]:
            self.draw_startup()
        elif button_clicked == button_names[9]:
            self.generate_default_highscores()
        elif button_clicked == button_names[10]:
            self.save_settings()
        elif button_clicked == button_names[11]:
            # self.draw_startup()
            print('Main Menu....')
        elif button_clicked == button_names[12]:
            self.new_game()
        elif button_clicked == button_names[13]:
            self.new_game()
            self.minesweeper_bot()

    def left_click(self, event):  

        x, y = self.__click_to_tile(event)
        index = self.tile_index(x, y)

        if self.game_state == Game_state.STARTUP:
            row = self.setting('row')
            col = self.setting('col')

            self.generate_board(row=row, col=col, bomb=self.setting('bomb'), initial=index)
            self.game_state = Game_state.GAME
        
        if self.game_state != Game_state.BOT:
            self.tile_action(i=index, action='open')
            
    def right_click(self, event):

        if self.game_state == Game_state.BOT: return

        x, y = self.__click_to_tile(event)
        index = self.tile_index(x, y)
        tile_val = self.seen_tiles[index]

        if tile_val == np.inf or tile_val == -np.inf:
            self.tile_action(i=index, action='flag')
    
    def middle_click(self, event):
        
        if self.game_state == Game_state.DONE: return
        if self.game_state == Game_state.BOT: return

        x, y = self.__click_to_tile(event)
        index = self.tile_index(x=x, y=y)

        tile_val = self.seen_tiles[index]
        if tile_val == np.inf or tile_val == -np.inf:
            self.tile_action(i=index, action='flag')
        elif tile_val != -1:

            n_tiles = self.get_surrounding_tiles(index)
            n_flagged = np.count_nonzero(self.seen_tiles[n_tiles] == -np.inf)

            if n_flagged == tile_val:
                to_open = []
                hidden_index = np.where(self.seen_tiles[n_tiles] == np.inf)[0]
                for i in hidden_index:
                    to_open.append(n_tiles[i])
                self.update_tiles(points=to_open, state='open')

    def tile_action(self, i, action='open'):

        if self.game_state == Game_state.DONE: return

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

    def new_game(self):
        self.game_time = 0
        self.__update_timer()
        self.flag_counter = self.__setting(self.dif, 2)
        self.__update_flags(0)
        self.game_state = Game_state.STARTUP
        self.canvas_board.delete("all")
        self.draw_tiles(row=self.setting('row'), col=self.setting('col'), w=self.setting('w'))

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


        ### Time indicator
        font=self.__get_font()
        fill=self.__setting('menu_color', 3)
        self.time_indicator = self.canvas.create_text(w, w/2, anchor=W, 
                                            font=font, fill=fill, text='')

        ### Flag indicator
        self.flag_indicator = self.canvas.create_text(w*(col + 1), w/2, anchor=E, 
                                            font=font, fill=fill, text='')
        
        ### New game button
        game_buttons = self.__setting('game_screen', -1)
        for i, index in enumerate(game_buttons):
            text = self.__setting('buttons', index)
            self.array_button.append(Button(canvas=self.canvas, 
                                        x=w*(i+1)/6 * (2*col +1), 
                                        y=int(w/8), 
                                        width=w,
                                        height=int(3/4*w),
                                        fill=self.__setting('menu_color', 0),
                                        fg=fill,
                                        bd=fill,
                                        font=self.__get_font(), 
                                        text=text,
                                        tag=text))
        
        self.new_game()

    def generate_board(self, row, col, bomb, initial):

        game_size = row*col

        tile_indexes = [i for i in range(game_size) if i != initial]
        bomb_indexes = np.random.choice(tile_indexes, size=bomb, replace=False)
        
        self.tile_values = np.zeros(game_size)
        self.tile_values[bomb_indexes] = -1
        self.tile_values = np.reshape(self.tile_values, (row, col))
        bomb_pos = np.copy(self.tile_values)
        bomb_counter = np.zeros(((row+2),(col+2)))

        for x, y in ((0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)):
            bomb_counter[x:x+row,y:y+col] += bomb_pos

        ### Remove earlier added padding, and set bomb_locations to 0
        bomb_counter = bomb_counter[1:-1,1:-1]
        bomb_counter[np.where(bomb_pos == -1)] = 0
        self.tile_values += np.abs(bomb_counter)
        self.tile_values = np.reshape(self.tile_values, game_size)
        self.draw_numbers(row=row, col=col)

        tile_width = self.setting('w')
        for i in range(col):
            for j in range(row):
                index = i + j*col
                self.canvas_board.create_text((i+1/2)*tile_width, (j+1/2)*tile_width, text= index)
        
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
                if text == -1: text = 0
                color = self.__setting('tile_color_num', int(text))
                text = '' if (text == 0 or text == -1) else int(text)
                self.drawn_tiles_num[index] = (
                        self.canvas_board.create_text((i+.5)*w, (j+.5)*w, 
                        text='{}'.format(text), 
                        font=self.__get_font(size=int(w/2)),
                        fill=color, state='hidden'))

    def update_tiles(self, points, state='hidden'):

        if self.game_state == Game_state.DONE: return

        points = np.array(points)

        if state == 'hidden':
            self.__update_flags(1)
            color = self.__setting('tile_color', 0)
            self.seen_tiles[points] = np.inf
            for p in points:
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)
        
        ### Open Tile
        elif state == 'open':

            self.window.update()
            text = np.array(self.tile_values[points])
            self.seen_tiles[points] = text
            
            ### Open all input bombs
            if -1 in text:
                to_open = []
                for i, p in np.ndenumerate(text):
                    if p != -1: continue
                    to_open.append(points[i])
                self.update_tiles(to_open, 'bomb')
                return
            
            to_open = []
            color = self.__setting('tile_color', 1)
            for i, p in np.ndenumerate(points):
                
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)
                self.canvas_board.itemconfig(self.drawn_tiles_num[p], state='normal')

                ### Add blank tiles to next round
                if self.seen_tiles[p] == 0:
                    sur_tiles = self.get_surrounding_tiles(points[i])                                
                    for d in sur_tiles:
                        if self.seen_tiles[d] == np.inf and d not in to_open:
                            to_open.append(d)
            if len(to_open) > 0:
                self.update_tiles(to_open, 'open')
                return

        ### Flag tile
        elif state == 'flag':
            self.__update_flags(-1)
            self.seen_tiles[points] = -np.inf
            color = self.__setting('tile_color', 2)
            for p in points:
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)
                self.completed_tiles[p] = True


        ### Causes Game Over
        elif state == 'bomb':
            ### TODO add game over code!
            color = self.__setting('tile_color', 3)
            for p in points:
                self.canvas_board.itemconfig(self.drawn_tiles[p], fill=color)
            self.game_state = Game_state.DONE
            print('Game Over')
        
        ### Check Victory
        n_hidden = np.count_nonzero(self.seen_tiles == np.inf)
        n_flags = np.count_nonzero(self.seen_tiles == -np.inf)
        if n_hidden + n_flags == self.setting('bomb'):
            self.game_state = Game_state.DONE
            print('Victory')

    def __update_flags(self, dif):
        self.flag_counter += dif
        self.canvas.itemconfig(self.flag_indicator,
                               text='{} \u2690'.format(self.flag_counter))

    def __update_timer(self):
        self.canvas.itemconfig(self.time_indicator, 
                                   text='\u23f3 {}'.format(self.game_time))

    def get_surrounding_tiles(self, index):
        
        i, j = self.tile_xy(index)
        col = self.setting('col')
        row = self.setting('row')
        points = []

        for x, y in ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)):
            dx, dy = i+x, j+y
            if (0 <= dx < row) and (0 <= dy < col):
                points.append(self.tile_index(dy, dx))
        return np.array(points)

    def mainloop(self):
        self.window.mainloop()

class Button():

    def __init__(self, x=0, y=0, width=10, height=10, text='', font=("Arial", 12), fill='#123123', canvas=None, tag=None, fg='#ffffff', bd='#000000'):
        
        self.canvas = canvas
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.fill = fill
        self.fg, self.bd = fg, bd
        self.font = font
        self.mouse_in_box = False
        self.tag = tag

        self.create_button()

    def create_button(self):
        self.button_area = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, fill=self.fill, outline=self.bd, width=2)
        self.button_text = self.canvas.create_text(self.x + self.width/2, self.y + self.height/2, text=self.text, font=self.font, fill=self.fg)

    def delete_button(self):
        self.canvas.delete(self.button_area)
        self.canvas.delete(self.button_text)
    
    def get_tag(self):
        return self.tag
    
    def set_tag(self, tag):
        self.tag = tag

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_name(self):
        return self.text

    def point_in_box(self, x, y):

        x_bool = (x >= self.x) and (x <= self.x + self.width)
        y_bool = (y >= self.y) and (y <= self.y + self.height)

        if x_bool and y_bool: return True
        else: return False
    
    def set_button_highlighted(self, state):
        self.mouse_in_box = state

    def get_button_highlighted(self):
        return self.mouse_in_box

game_instance = Minesweeper()
game_instance.mainloop()