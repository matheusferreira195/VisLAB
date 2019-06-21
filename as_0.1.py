import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import *
import win32com.client as com

root = tk.Tk()


#Inicialização do VISSIM

'''Vissim = com.Dispatch("Vissim.Vissim") #abre o vissim

path = os.path.join(os.getcwd(), 'test.inpx') #seta o diretorio do .inpx

Vissim.LoadNet(path, False) #carrega a rede no vissim
'''
#Barra horizontal menu


def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()

menubar = Menu(root)

menubar.add_command(label="Open", command=donothing)

menubar.add_command(label="Save", command=donothing)

menubar.add_command(label="Save as...", command=donothing)

options_menu = Menu(menubar, tearoff = 0)
menubar.add_cascade(label="Options", menu = options_menu)

sa_menu = Menu(menubar, tearoff = 0)
menubar.add_cascade(label="Sensitivity Analysis", menu = sa_menu)

calib_menu = Menu(menubar, tearoff = 0)
menubar.add_cascade(label="Calibration", menu = calib_menu)

val_menu = Menu(menubar, tearoff = 0)
menubar.add_cascade(label="Validation", menu = val_menu)

help_menu = Menu(menubar, tearoff = 0)
menubar.add_cascade(label="Help", menu = help_menu)

root.config(menu=menubar)
root.mainloop()



