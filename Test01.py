import tkinter as tk
from tkinter import Canvas, ttk
from scripts.serialreadtestVdev import *
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as anim 
from PIL import ImageTk, Image
from tkinter import filedialog

import threading
import os


class TestPage(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        connectSerial("COM4")

        self.version = "0.0.2"
        self.geometry("600x600")
        self.title("Test Page 01")
        self.resizable(1, 1)
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=5)
        container.grid_columnconfigure(0, weight=5)

        self.frames = {}

        for F in (PageOne, PageTwo):
            frame = F(container, self) 
            self.frames[F] = frame 
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(PageOne)
    
    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()
    


class PageOne(tk.Frame):


    def __init__(self, parent, controller):

        ttk.Frame.__init__(self, parent)

        RUN_TEST = ttk.Button(self, text="Graficar", 
                              command=lambda: controller.show_frame(PageTwo)
                              )
        RUN_TEST.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
    



class PageTwo(tk.Frame):


    def __init__(self, parent, controller):

        ttk.Frame.__init__(self, parent)
        
        def openfn():
            filename = filedialog.askopenfilename(title='open')
            print(filename)
            return filename

        def open_img():
            x = openfn()
            img = Image.open(x)
            img = img.resize((250, 250), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            panel = tk.Label(self, image=img)
            panel.image = img
            panel.pack()

        btn = tk.Button(self, text='open image', command=open_img).pack()



        



app = TestPage()

app.mainloop()