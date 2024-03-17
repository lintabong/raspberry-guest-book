import os
import tkinter
import threading
import sounddevice

from tkinter import messagebox

from helper import config
from helper import fileManager


configuration = config.read()

h   = configuration["height"]
w   = configuration["width"]
cfh = configuration["controll"]["height"]


class MainFrame(tkinter.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.config(width=w, height=h-cfh, background="#B7BDDE")
        self.place(x=0, y=0)

        self.activeDir = ""

        self.fileFrame()

    def fileFrame(self):
        listframe = tkinter.Frame(self, width=w-40, height=h-(cfh+65), background="#B7BDDE")
        listframe.place(x=20, y=45)
        
        self.listDirectories = tkinter.Listbox(
            listframe, 
            height=8, 
            width=25,
            selectmode=tkinter.SINGLE)
        
        self.listFiles = tkinter.Listbox(
            listframe, 
            height=8, 
            width=25,
            selectmode=tkinter.SINGLE)
        
        tkinter.Button(
            listframe,
            text=">>",
            width=10, 
            height=2,
            command=self.openDir).place(x=235, y=62)
        
        tkinter.Button(
            listframe,
            text="Delete",
            width=10, 
            height=2,
            command=self.deleteSound).place(x=365, y=200)
        
        tkinter.Button(
            listframe,
            text="Play",
            width=10, 
            height=2,
            command=self.pathSound).place(x=465, y=200)
        
        tkinter.Button(
            listframe,
            text="Copy to Flashdisk",
            width=20, 
            height=2,
            command=self.copyDir).place(x=0, y=200)

        self.listDirectories.place(x=0, y=0)
        self.listFiles.place(x=355, y=0)

        self.listDirectories.delete(0, tkinter.END)
        self.listFiles.delete(0, tkinter.END)

        for i, dir in enumerate(os.listdir("./result")):
            self.listDirectories.insert(i, dir)

    def deleteSound(self):
        pass

    def pathSound(self):
        try:
            for i in self.listFiles.curselection():
                select = self.listFiles.get(i)

            self.filepath = fileManager.getSound(f'result/{self.activeDir}/{select}')

            threading.Thread(target=self.playSound).start()

        except UnboundLocalError:
            messagebox.showerror("Error", "please chose audio on left listview")

    def playSound(self):
        sounddevice.play(self.filepath, 44100, device=3)
        sounddevice.wait()

    def openDir(self):
        for i in self.listDirectories.curselection():
            self.activeDir = self.listDirectories.get(i)

        self.listFiles.delete(0, tkinter.END)

        for i, file in enumerate(os.listdir(f'./result/{self.activeDir}')):
            self.listFiles.insert(i, file)

    def copyDir(self):
        pass


class HomeFrame(tkinter.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.config(width=w, height=h-cfh, background="#219ebc")
        self.place(x=0, y=cfh)

        MainFrame(self)