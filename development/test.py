import win32com.client as com
import pandas as pd

Vissim = com.Dispatch('Vissim.Vissim')
#Vissim = com.Dispatch("Vissim.Vissim") #Abrindo o Vissim
path_network =r'E:\Google Drive\Scripts\vistools\development\net\teste\teste.inpx'
flag = False 
Vissim.LoadNet(path_network, flag) #Carregando o arquivo
#ctypes.windll.user32.MessageBoxW(0, "Net loaded", "Vissim ready", 1)
print('net loaded\n')


Vissim.Simulation.SetAttValue('RandSeed', 42)

Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode

n_dc = 5

for i in range(10):
    Vissim.Simulation.SetAttValue('RandSeed', 42+i)
    
    Vissim.Simulation.RunContinuous() 
    
    mer = r'E:\Google Drive\Scripts\vistools\development\net\teste\teste_001.mer'
    mer_data_raw = pd.read_csv(mer, sep=';', skiprows=(8+n_dc), skipinitialspace=True, index_col=False)
    mer_data = mer_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    mer_data.to_csv(r'E:\Google Drive\Scripts\vistools\development\net\teste\output%i.csv' % (i),sep=';')