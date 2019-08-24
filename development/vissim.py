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

def datapoint_normalizer(dataset):
    output=[]
    for index, item in enumerate(dataset):
        if item[0] == '':
            output.append(str('N/A') + ' / #'+ str(item[1]))
        else:
            output.append(str(item[0]) + ' / #'+ str(item[1]))
    return output


def datapoint_info(type):
    attribute=['Name', 'No']

    if type == 'data_collector':
        data_collectors_raw = Vissim.Net.DataCollectionPoints.GetMultipleAttributes(attribute)
        data_collectors = datapoint_normalizer(data_collectors_raw)
        return data_collectors

    if type == 'queue_counter':
        queue_counters_raw = Vissim.Net.QueueCounters.GetMultipleAttributes(attribute)
        queue_counters = datapoint_normalizer(queue_counters_raw)
        return queue_counters

    else:
        travel_times_raw = Vissim.Net.VehicleTravelTimeMeasurements.GetMultipleAttributes(attribute)
        travel_times = datapoint_normalizer(travel_times_raw)
        return travel_times

print(datapoint_info('data_collector'))

Vissim = None