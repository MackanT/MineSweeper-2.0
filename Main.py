from tkinter import *
from enum import Enum
from PIL import Image, ImageTk
import os
import csv
import threading
import numpy as np
import time
from Buttons import Button, Slide_Button

cwd = os.getcwd()

startup_width = 600
startup_height = 400
game_border = 50


class Game_state(Enum):
    MENU = 0
    STARTUP = 1
    GAME = 2
    DONE = 3


class Minesweeper():

    def __init__(self):

        # Initial Game State
        self.game_state = Game_state.STARTUP

        # Load Application Data
        self.dif = 'hard'
        self.game_parameters = self.__load_settings('settings')
        self.array_button = []
        self.enable_graphics = True

        # Screen Settings
        self.window = Tk()
        self.window.title('The Electric Boogaloo - Minesweeper 2')
        self.window.config(bg=self.__setting('menu_color', 0))
        self.canvas = Canvas(self.window,
                             width=self.__setting('size', 0),
                             height=self.__setting('size', 1),
                             bg=self.__setting('menu_color', 0),
                             borderwidth=0,
                             highlightthickness=0
                             )
        self.canvas_board = Canvas(self.window,
                                   width=0,
                                   height=0,
                                   highlightthickness=2,
                                   highlightcolor=self.__setting(
                                       'menu_color', 3)
                                   )
        self.test_canvas = []

        # Graphical Loading
        self.start_up_splash = self.get_image('startup')

        # TODO add menu creating below

        self.canvas.bind('<Motion>', self.moved_mouse)
        self.canvas.bind('<Button-1>', self.button_click)
        self.canvas_board.bind('<Button-1>', self.left_click)
        self.canvas_board.bind('<Button-2>', self.middle_click)
        self.canvas_board.bind('<Button-3>', self.right_click)
        self.canvas_board.bind('<space>', self.middle_click)
        self.canvas_board.bind('<r>', self.restart)
        self.canvas_board.focus_set()

        self.window.resizable(False, False)
        self.canvas.pack()

        self.generate_menu()

        self.start_timer()

        # self.test_code()

    def generate_menu(self):

        self.game_state = Game_state.MENU
        self.canvas.delete('all')

        self.canvas.config(width=startup_width, height=startup_height)
        self.window.geometry('{}x{}'.format(startup_width, startup_height))

        self.draw_buttons(x=startup_width/2, y=0, x_move=-50,
                          list='main_menu', button=Slide_Button)
        self.canvas.create_image(game_border, startup_height/2, anchor=W,
                                 image=self.start_up_splash)

    def draw_buttons(self, x, y, border=10, list=None, vertical=True, button=Button, x_move=0, y_move=0):

        button_len = 5

        list = np.zeros(button_len, dtype=object)
        for i in range(button_len):
            list[i] = self.__setting('buttons', -1)[i]

        dx = 0 if vertical else 1
        dy = 1 if vertical else 0

        width = dy*(startup_width - x - 2*border) + dx * \
            int(((startup_width-x)-(button_len+1)*border)/button_len)
        height = dx*(startup_height - y - 2*border) + dy * \
            int(((startup_height-y)-(button_len+1)*border)/button_len)

        for i, name in enumerate(list):
            x_pos = x + i*dx*(width) + dx*(i+1)*border
            y_pos = y + i*dy*(height) + dy*(i+1)*border
            self.array_button.append(
                button(
                    canvas=self.canvas,
                    x_pos=x_pos,
                    y_pos=y_pos,
                    width=width,
                    height=height,
                    text=name,
                    fill=self.__setting('menu_color', 1),
                    font=self.__get_font(),
                    x_anim=x_move,
                    y_anim=y_move
                )
            )

    def test_code(self):
        self.draw_game(row=15, col=30)
        self.generate_board(row=15, col=30, bomb=99, initial=15)
        tile_check = [10, 11, 40, 51, 50, 12, 13, 5,
                      7, 17, 89, 9, 19, 22, 41, 42, 43, 44, 45]
        temp_board = self.seen_tiles
        n = self.get_surrounding_tiles(15)
        surrounding_tiles = []

        for tile in tile_check:
            surrounding_tiles.append([tile, self.get_surrounding_tiles(tile)])

        in_time = time.time()
        for i in range(1000000):

            surround_index = self.get_neighbours(10, surrounding_tiles)

        print('Time ellapsed: {} s'.format(time.time()-in_time))

    # Images

    def get_image(self, filename, folder='images'):

        file_name = cwd + '\\' + folder + '\\' + filename + '.png'
        return PhotoImage(file=file_name)

    # Timer Functions

    def start_timer(self):
        threading.Timer(1.0, self.start_timer).start()
        if self.game_state == Game_state.GAME:
            self.game_time += 1
            self.__update_timer()

    # Game Logic / Behing the scenes

    def __get_font(self, size=20, bold=True):
        if bold:
            return ("GOST Common", size, "bold")
        else:
            return ("GOST Common", size)

    def __setting(self, name, index):
        """ returns setting 'name' with position 'index' """
        for row in self.game_parameters:
            if row[0] == name:
                if index == -1:
                    return row[1]
                return row[1][index]
        return False

    def __load_settings(self, folder):
        """ returns list of lists with loaded settings. Loaded file: cwd\\folder.csv """

        file_name = cwd + '\\{}.csv'.format(folder)

        # TODO Add crash/try something if file does not exist!
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

    # User Input

    def __click_to_tile(self, event):
        w = self.setting('w')
        x = int(event.x/w)
        y = int(event.y/w)
        if x >= self.setting('col'):
            return -1, -1  # Detect if outside of play area
        if y >= self.setting('row'):
            return -1, -1
        return x, y

    def find_clicked_button(self, x, y):
        for i, item in enumerate(self.array_button):
            if item.point_in_box(x, y):
                return self.array_button[i].get_name()

    def button_click(self, event):

        button_clicked = self.find_clicked_button(event.x, event.y)
        if button_clicked == None:
            return
        button_names = self.__setting('buttons', -1)

        if button_clicked == button_names[0]:
            self.canvas.delete('all')
            self.array_button = []
            self.draw_game(col=self.setting('col'), row=self.setting('row'))
        elif button_clicked == button_names[1]:
            print('stats')
            # self.menu_statistics()
        elif button_clicked == button_names[2]:
            print('setting')
            # self.menu_settings()
        elif button_clicked == button_names[3]:
            print('credits')
            # self.menu_credits()
        elif button_clicked == button_names[4]:
            print('quit')
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
            self.canvas.delete('all')
            self.canvas_board.place_forget()
            self.array_button = []
            self.generate_menu()
        elif button_clicked == button_names[12]:
            self.new_game()
            print('clicked here')
        elif button_clicked == button_names[13]:
            self.new_game()
            self.minesweeper_bot()

    def left_click(self, event):

        x, y = self.__click_to_tile(event)
        if x == -1 or y == -1:
            return
        index = self.tile_index(x, y)

        if self.game_state == Game_state.STARTUP:
            row = self.setting('row')
            col = self.setting('col')

            self.generate_board(
                row=row, col=col, bomb=self.setting('bomb'), initial=index)
            self.game_state = Game_state.GAME

        self.tile_action(i=index, action='open')

    def right_click(self, event):

        x, y = self.__click_to_tile(event)
        if x == -1 or y == -1:
            return
        index = self.tile_index(x, y)
        tile_val = self.seen_tiles[index]

        if tile_val == np.inf or tile_val == -np.inf:
            self.tile_action(i=index, action='flag')

    def middle_click(self, event):

        if self.game_state == Game_state.DONE:
            return

        x, y = self.__click_to_tile(event)
        if x == -1 or y == -1:
            return
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

    def moved_mouse(self, event):
        """ Fired by mouse movement, calls appropriate function depending on game state """
        if (self.game_state == Game_state.MENU):
            x, y = event.x, event.y
            for button in self.array_button:
                if button.point_in_box(x, y):
                    # First highlighted
                    if not button.get_button_highlighted():
                        # self.play_sound('home_button')
                        button.set_button_highlighted(True)
                        button.is_selected(True)
                    # Mouse remains on button
                    else:
                        button.set_button_highlighted(True)
                else:
                    # Mouse leaves button
                    if button.get_button_highlighted():
                        button.is_selected(False)
                    # Mouse is outside of button
                    button.set_button_highlighted(False)

    def tile_action(self, i, action='open'):

        if self.game_state == Game_state.DONE:
            return

        if action == 'open':
            if not self.__is_flagged(i):
                self.update_tiles(points=i, state='open')

        elif action == 'flag':
            if self.__is_open(i):
                return
            if self.__is_flagged(i):
                self.update_tiles(points=i, state='hidden')
            elif not self.__is_flagged(i):
                self.update_tiles(points=i, state='flag')

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

    # Initialize Game

    def restart(self, event):
        self.new_game()

    def new_game(self):
        self.game_time = 0
        self.flag_counter = self.__setting(self.dif, 2)
        self.game_state = Game_state.STARTUP

        if self.enable_graphics:
            self.__update_timer()
            self.__update_flags(0)
            self.canvas_board.delete("all")
            self.draw_tiles(row=self.setting('row'),
                            col=self.setting('col'), w=self.setting('w'))

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
        self.window.geometry('%dx%d' % ((col+2)*w, (row+2)*w))
        self.canvas_board.place(x=w, y=w, anchor=NW)

        # Time indicator
        font = self.__get_font()
        fill = self.__setting('menu_color', 3)
        self.time_indicator = self.canvas.create_text(w, w/2, anchor=W,
                                                      font=font, fill=fill, text='')

        # Flag indicator
        self.flag_indicator = self.canvas.create_text(w*(col + 1), w/2, anchor=E,
                                                      font=font, fill=fill, text='')

        # New game button
        game_buttons = self.__setting('game_screen', -1)
        for i, index in enumerate(game_buttons):
            text = self.__setting('buttons', index)
            self.array_button.append(Button(canvas=self.canvas,
                                            x=w*(i+1)/6 * (2*col + 1),
                                            y=int(w/8),
                                            width=w,
                                            height=int(3/4*w),
                                            fill=self.__setting(
                                                'menu_color', 0),
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
        bomb_counter = np.zeros(((row+2), (col+2)))

        for x, y in ((0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)):
            bomb_counter[x:x+row, y:y+col] += bomb_pos

        # Remove earlier added padding, and set bomb_locations to 0
        bomb_counter = bomb_counter[1:-1, 1:-1]
        bomb_counter[np.where(bomb_pos == -1)] = 0
        self.tile_values += np.abs(bomb_counter)
        self.tile_values = np.reshape(self.tile_values, game_size)

        if self.enable_graphics:
            self.draw_numbers(row=row, col=col)

    def draw_win_screen(self):

        dx = int(self.canvas_board.winfo_width()/2)
        dy = int(self.canvas_board.winfo_height()/2)
        w = self.setting('w') + 10

        self.draw_rectangle(dx - 3*w, dy - w, dx + 3*w,
                            dy + w, fill='#fbd083', alpha=.6)
        self.canvas_board.create_text(
            dx, dy-5, anchor=S, text='Congratulations!', font=self.__get_font())
        win_text = 'You completed the \n game in {0} seconds!'.format(
            self.game_time)

        self.canvas_board.create_text(
            dx, dy+5, anchor=N, text=win_text, font=self.__get_font(size=12), justify=CENTER)

    def draw_lose_screen(self):

        dx = int(self.canvas_board.winfo_width()/2)
        dy = int(self.canvas_board.winfo_height()/2)
        w = self.setting('w') + 10

        self.draw_rectangle(dx - 3*w, dy - w, dx + 3*w,
                            dy + w, fill='#ed2939', alpha=.8)
        self.canvas_board.create_text(
            dx, dy-5, anchor=S, text='Failure!', font=self.__get_font())
        self.canvas_board.create_text(
            dx, dy+5, anchor=N, text='You failed in securing the mines!', font=self.__get_font(size=12), justify=CENTER)

    def draw_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = (int(fill[1:3], 16), int(fill[3:5], 16),
                    int(fill[5:7], 16), alpha)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            self.test_canvas.append(ImageTk.PhotoImage(image))
            self.canvas_board.create_image(
                x1, y1, image=self.test_canvas[-1], anchor='nw')
        return self.canvas_board.create_rectangle(x1, y1, x2, y2, **kwargs)

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
                if text == -1:
                    text = 0
                color = self.__setting('tile_color_num', int(text))
                text = '' if (text == 0 or text == -1) else int(text)
                self.drawn_tiles_num[index] = (
                    self.canvas_board.create_text((i+.5)*w, (j+.5)*w,
                                                  text='{}'.format(text),
                                                  font=self.__get_font(
                                                      size=int(w/2)),
                                                  fill=color, state='hidden'))

    def update_tiles(self, points, state='hidden'):

        if self.game_state == Game_state.DONE:
            return

        points = np.array(points)
        if np.size(points) == 0:
            return False

        if state == 'hidden':
            self.__update_flags(1)
            self.seen_tiles[points] = np.inf

            if self.enable_graphics:
                color = self.__setting('tile_color', 0)
                for i, p in np.ndenumerate(points):
                    self.canvas_board.itemconfig(
                        self.drawn_tiles[p], fill=color)

        # Open Tile
        elif state == 'open':

            text = np.array(self.tile_values[points])
            self.seen_tiles[points] = text

            # Open all input bombs
            if -1 in text:
                to_open = []
                for i, p in np.ndenumerate(text):
                    if p != -1:
                        continue
                    to_open.append(points[i])
                self.update_tiles(to_open, 'bomb')
                return

            to_open = []
            color = self.__setting('tile_color', 1)
            for i, p in np.ndenumerate(points):

                if self.enable_graphics:
                    self.canvas_board.itemconfig(
                        self.drawn_tiles[p], fill=color)
                    self.canvas_board.itemconfig(
                        self.drawn_tiles_num[p], state='normal')

                # Add blank tiles to next round
                if self.seen_tiles[p] == 0:
                    sur_tiles = self.get_surrounding_tiles(points[i])
                    for d in sur_tiles:
                        if self.seen_tiles[d] == np.inf and d not in to_open:
                            to_open.append(d)
            if len(to_open) > 0:
                self.update_tiles(to_open, 'open')
                return

        # Flag tile
        elif state == 'flag':
            self.__update_flags(-1)
            self.seen_tiles[points] = -np.inf

            if self.enable_graphics:
                color = self.__setting('tile_color', 2)
                for i, p in np.ndenumerate(points):
                    self.canvas_board.itemconfig(
                        self.drawn_tiles[p], fill=color)

        # Causes Game Over
        elif state == 'bomb':

            self.game_state = Game_state.DONE
            self.win_state = False

            if self.enable_graphics:
                color = self.__setting('tile_color', 3)
                for p in points:
                    self.canvas_board.itemconfig(
                        self.drawn_tiles[p], fill=color)
                self.draw_lose_screen()

            return

        # Check Victory
        n_hidden = np.count_nonzero(self.seen_tiles == np.inf)
        n_flags = np.count_nonzero(self.seen_tiles == -np.inf)
        if n_hidden + n_flags == self.setting('bomb'):
            self.game_state = Game_state.DONE
            self.win_state = True

            if self.enable_graphics:
                self.draw_win_screen()

        return True

    def __update_flags(self, dif):
        self.flag_counter += dif
        if not self.enable_graphics:
            return
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

        for x, y in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            dx, dy = i+x, j+y
            if (0 <= dx < row) and (0 <= dy < col):
                points.append(self.tile_index(dy, dx))
        return np.array(points)

    def mainloop(self):
        self.window.mainloop()


game_instance = Minesweeper()
game_instance.mainloop()
