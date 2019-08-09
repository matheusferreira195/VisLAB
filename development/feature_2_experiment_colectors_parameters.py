#This file contains the field that will allow the user to select evaluation points and variables


import pandas as pd, win32com.client as com, win32gui, os, win32con
from tkinter import *

#Opens Vissim and load the net data
Vissim = com.Dispatch("Vissim.Vissim")
#Vissim.Visible = 0

hwnd = win32gui.FindWindow(None, "PTV Vision Traffic & Pedestrian Simulation")  # Class or title
win32gui.ShowWindow(hwnd, win32con.SW_HIDE) # Hide via Win32Api
Path = os.getcwd()
rede = r'E:\Google Drive\Scripts\vistools\development\net\teste.inpx' #os.path.join(Path, 'teste.inpx')

Vissim.LoadNet(rede,False)

#Query Vissim for a tuple with the name and id of data collectors, queue collectors and time travel collectors

Attributes=['Name','No']

data_collectors = Vissim.Net.DataCollectionPoints.GetMultipleAttributes(Attributes)
queue_counters = Vissim.Net.QueueCounters.GetMultipleAttributes(Attributes)
traveltime_collectors = Vissim.Net.VehicleTravelTimeMeasurements.GetMultipleAttributes(Attributes)

print(data_collectors)
print(queue_counters)
print(traveltime_collectors)



class Experiment:
    pass

class Colectors(Experiment):
    def __init__ (self, object_type, name, no, perf_variable, time_interval):
        self.object_type = object_type
        self.name = name
        self.no = no
        self.perf_variable = perf_variable
        self.time_interval = time_interval

class Parameters(Experiment):
    def __init__ (self, parameter, inf_lim, sup_lim, step):
        self.parameter = parameter
        self.inf_lim = inf_lim
        self.sup_lim = sup_lim
        self.step = step

        