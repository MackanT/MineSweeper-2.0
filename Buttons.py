from tkinter import *
from tkinter import font


class Button:

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
        self.button_area = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height, fill=self.fill, outline=self.bd, width=2)
        self.button_text = self.canvas.create_text(
            self.x + self.width/2, self.y + self.height/2-2, text=self.text, font=self.font, fill=self.fg)

    def delete_button(self):
        self.canvas.delete(self.button_area)
        self.canvas.delete(self.button_text)

    def get_tag(self):
        return self.tag

    def set_tag(self, tag):
        self.tag = tag

    def get_x(self):
        return self.x_pos

    def get_y(self):
        return self.y_pos

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_name(self):
        return self.text

    def point_in_box(self, x, y):

        x_bool = (x >= self.x) and (x <= self.x + self.width)
        y_bool = (y >= self.y) and (y <= self.y + self.height)

        if x_bool and y_bool:
            return True
        else:
            return False

    def set_button_highlighted(self, state):
        self.mouse_in_box = state

    def get_button_highlighted(self):
        return self.mouse_in_box


class Slide_Button(Button):

    def __init__(self, x_pos=0, y_pos=0, width=10, height=10, text='', font=None, fill=None, canvas=None, x_anim=0, y_anim=0):

        super().__init__(x_pos, y_pos, width, height, text, font, fill, canvas)

        self.x_anim = x_anim
        self.y_anim = y_anim

    def is_selected(self, state):
        if state:
            self.canvas.move(self.button_area, self.x_anim, self.y_anim)
            self.canvas.move(self.button_text, self.x_anim, self.y_anim)
        else:
            self.canvas.move(self.button_area, -self.x_anim, -self.y_anim)
            self.canvas.move(self.button_text, -self.x_anim, -self.y_anim)


class Pop_Button(Button):

    def __init__(self, x_pos=0, y_pos=0, width=10, height=10, text='', font=None, fill=None, canvas=None, x_anim=0, y_anim=0):

        super().__init__(x_pos, y_pos, width, height, text, font, fill, canvas)

        self.x_anim = x_anim
        self.y_anim = y_anim

    def is_selected(self, state):

        x0, y0, x1, y1 = self.canvas.coords(self.button_area)

        if state:
            self.canvas.coords(self.button_area, x0-self.x_anim,
                               y0-self.y_anim, x1+self.x_anim, y1+self.y_anim)
        else:
            self.canvas.coords(self.button_area, x0+self.x_anim,
                               y0+self.y_anim, x1-self.x_anim, y1-self.y_anim)


class Toggle_Switch:

    def __init__(self, x_pos=0, y_pos=0, width=150, height=50, state=True, fill=['#565554', '#cfd0d2', '#fbd083'], canvas=None, font=None):

        self.canvas = canvas
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.fill = fill
        self.state = state
        self.font = font

        self.create_switch()

    def create_switch(self):
        size = 5

        self.button_area = self.canvas.create_rectangle(
            self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height, fill=self.fill[1])
        self.button_toggle = self.canvas.create_rectangle(
            self.x_pos+size, self.y_pos+size, self.x_pos + self.width/2-size, self.y_pos + self.height-size, fill=self.fill[2])
        self.button_text = self.canvas.create_text(
            self.x_pos + self.width/4, self.y_pos + self.height/2, text='ON', font=self.font, fill=self.fill)

        if not self.state:
            self.toggle_switch(state=self.state)

    def toggle_switch(self, state=None):

        if state == None:
            self.state = not self.state
        else:
            self.state = state

        if self.state:
            self.canvas.move(self.button_toggle, -self.width/2, 0)
            self.canvas.move(self.button_text, -self.width/2, 0)
            self.canvas.itemconfig(self.button_toggle, fill=self.fill[2])
            self.canvas.itemconfig(self.button_text, text='ON')
        else:
            self.canvas.move(self.button_toggle, self.width/2, 0)
            self.canvas.move(self.button_text, self.width/2, 0)
            self.canvas.itemconfig(self.button_toggle, fill=self.fill[1])
            self.canvas.itemconfig(self.button_text, text='OFF')

    def point_in_box(self, x, y):

        x_bool = (x >= self.x_pos) and (x <= self.x_pos + self.width)
        y_bool = (y >= self.y_pos) and (y <= self.y_pos + self.height)

        if x_bool and y_bool:
            return True
        else:
            return False


class Slider:

    def __init__(self, x=0, y=0, width=400, height=50, value=0, canvas=None, fill=['#cfd0d2', '#fbd083', '#fbd083'], font=None):

        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.canvas = canvas
        self.fill = fill
        self.font = font
        self.value = value

        self.draw_slider()

    def draw_slider(self):

        border = 5

        self.min = self.x + border
        self.dx = ((self.x - border + self.w - self.h - self.min)/100)

        self.slider_area = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.w, self.y + self.h, fill=self.fill[0])

        self.slider = self.canvas.create_rectangle(self.min,
                                                   self.y + border,
                                                   self.min + self.h,
                                                   self.y + self.h - border,
                                                   fill=self.fill[1])
        self.slider_text = self.canvas.create_text(
            self.x - 5, self.y + self.h/2, anchor=E, text=self.value, font=self.font, fill=self.fill)
        self.move_slider(0, val=self.value)

    def move_slider(self, x, val=None):

        if val == None:
            self.value = 100*(x - self.x)/self.w
        position = self.value*self.dx + self.min
        ___, y0, ___, y1 = self.canvas.coords(self.slider)
        self.canvas.coords(self.slider, position, y0, position + self.h, y1)
        self.canvas.itemconfig(self.slider_text, text=int(self.value))

    def point_in_box(self, x, y):

        x_bool = (x >= self.x) and (x <= self.x + self.w)
        y_bool = (y >= self.y) and (y <= self.y + self.h)

        if x_bool and y_bool:
            return True
        else:
            return False
