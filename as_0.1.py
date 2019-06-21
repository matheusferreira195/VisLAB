import os
import pandas as pd
import numpy as np
import tkinter as tk
import win32com.client as com


#Inicialização do VISSIM
Vissim = com.Dispatch("Vissim.Vissim") #abre o vissim
path = os.path.join(os.getcwd(), 'test.inpx') #seta o diretorio do .inpx
Vissim.LoadNet(path, False) #carrega a rede no vissim

#



