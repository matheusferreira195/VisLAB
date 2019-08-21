import win32com.client as com
import os
import ctypes  # An included library with Python install.

Vissim = com.Dispatch("Vissim.Vissim") #Abrindo o Vissim
path_network = r'E:\Google Drive\Scripts\vistools\development\net\teste.inpx'
flag = False 
Vissim.LoadNet(path_network, flag) #Carregando o arquivo
#ctypes.windll.user32.MessageBoxW(0, "Net loaded", "Vissim ready", 1)
print('net loaded\n')

#data collectors query
def datapoint_info(type):
    attribute=['Name', 'No']

    if type == 'data_collector':
        data_collectors = Vissim.Net.DataCollectionPoints.GetMultipleAttributes(attribute)
        return data_collectors
    if type == 'queue_counter':
        queue_counters = Vissim.Net.QueueCounters.GetMultipleAttributes(attribute)
        return queue_counters
    else:
        travel_times = Vissim.Net.VehicleTravelTimeMeasurements.GetMultipleAttributes(attribute)
        return travel_times
print(datapoint_info('data_collector'))

Vissim = None