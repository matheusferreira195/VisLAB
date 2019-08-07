#This file contains the net search method
import pandas as pd, win32com.client as com, win32gui, os, win32con

#Opens Vissim and load the net data
Vissim = com.Dispatch("Vissim.Vissim")
#Vissim.Visible = 0

hwnd = win32gui.FindWindow(None, "PTV Vision Traffic & Pedestrian Simulation")  # Class or title
win32gui.ShowWindow(hwnd, win32con.SW_HIDE) # Hide via Win32Api
Path = os.getcwd()
rede = r'E:\Google Drive\Scripts\vistools\development\teste.inpx' #os.path.join(Path, 'teste.inpx')

Vissim.LoadNet(rede,False)

#Query Vissim for a tuple with the name and id of data collectors, queue collectors and time travel collectors

Attributes=['Name','No']

data_collectors = Vissim.Net.DataCollectionPoints.GetMultipleAttributes(Attributes)
queue_counters = Vissim.Net.QueueCounters.GetMultipleAttributes(Attributes)
traveltime_collectors = Vissim.Net.VehicleTravelTimeMeasurements.GetMultipleAttributes(Attributes)

print(data_collectors)
print(queue_counters)
print(traveltime_collectors)
Vissim = None