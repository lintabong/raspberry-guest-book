import tkinter
from tkinter import messagebox

from helper import config
from helper.constant import *

from view.home import HomeFrame

configuration = config.read()
h   = configuration["height"]
w   = configuration["width"]
cfh = configuration["controll"]["height"]

class ControlFrame(tkinter.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.container = container

        self.config(width=w, height=cfh, background="#023047")
        self.place(x=0, y=0)

        tkinter.Button(
            self,
            text="Home",
            width=10,
            height=2,
            command=self.goHome).place(x=w-300, y=12)

        tkinter.Button(
            self,
            text="Config",
            width=10, 
            height=2,
            command=self.goConfig).place(x=w-200, y=12)

        tkinter.Button(
            self,
            text="Exit",
            width=10, 
            height=2,
            command=self.goDestroy).place(x=w-100, y=12)

        self.frames = {}
        self.frames[0] = HomeFrame(container)

        frame = self.frames[0]
        frame.tkraise()

    def goHome(self):
        frame = self.frames[0]
        frame.tkraise()

    def goConfig(self):
        frame = self.frames[1]
        frame.tkraise()

    def goDestroy(self):
        answer = messagebox.askyesno(title="Confirmation", message="Are you sure that you want to quit?")
        if answer:
            self.container.destroy()