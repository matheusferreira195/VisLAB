#This is the second window that the user should see. It allows the user to configure a 'experiment',
#selecting first the net data collectors and its net perfomance measure (npm), and also 
#the driving behavior's parameters and the search range.


import win32com.client as com
import tkinter as tk
from tkinter import ttk
from tkinter import *
import pandas as pd
import os
import itertools as it
import numpy as np
from saturation_headway import calculate_shdwy


NORM_FONT= ("Roboto", 10)
#check_icon = r'C:\Users\Matheus Ferreira\Google Drive\Scripts\vistools\resources\check.png'
#-------------------------------------------------------------------
Vissim = com.Dispatch('Vissim.Vissim')
#Vissim = com.Dispatch("Vissim.Vissim") #Abrindo o Vissim
path_network =r'E:\Google Drive\Scripts\vistools\development\net\teste.inpx'
flag = False 
Vissim.LoadNet(path_network, flag) #Carregando o arquivo
#ctypes.windll.user32.MessageBoxW(0, "Net loaded", "Vissim ready", 1)
print('net loaded\n')

attributes_tt = ['Start', 'End']

#time_intervals = Vissim.Net.TimeIntervalSets.ItemByKey(1).TimeInts.GetMultipleAttributes('TimeIntervalSet')

#print(time_intervals)
#--------------------------------------------------------------------


#function that models a popupmsg
def popupmsg(msg):
        popup = tk.Tk()
        popup.wm_title("!")
        label = ttk.Label(popup, text=msg, font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()

#-----------------------------------------------------------------------
#Query functions that pull from vissim metadata about the data points and creates a dataframe

def generate_dcdf():

    dc_df = pd.DataFrame(columns = ['Type', 'Name', 'No', 'Display'])
    attribute=['Name', 'No']
    attributes_dcm=['Name', 'No', 'DataCollectionPoints']
    attributes_ttm=['Name', 'No', 'VehTravTmMeas']
    data_collectors_measurements_raw = Vissim.Net.DataCollectionMeasurements.GetMultipleAttributes(attributes_dcm)
    queue_counters_raw = Vissim.Net.QueueCounters.GetMultipleAttributes(attribute)
    travel_time_measurements_raw = Vissim.Net.DelayMeasurements.GetMultipleAttributes(attributes_ttm)

    for item in data_collectors_measurements_raw:

        if len(item[0]) == 0:
            data = {'Type':'Data Collector', 'Name':'Empty', 'No':item[1], 'Data Collection Points':item[2], 'Display':('Data Collector' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Data Collector', 'Name':item[0], 'No':item[1], 'Data Collection Points':item[2], 'Display':('Data Collector' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)

    for item in queue_counters_raw:
        if len(item[0]) == 0:
            data = {'Type':'Queue Counter', 'Name':'Empty', 'No':item[1], 'Display':('Queue Counter' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Queue Counter', 'Name':item[0], 'No':item[1], 'Display':('Queue Counter' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)

    for item in travel_time_measurements_raw:
        if len(item[0]) == 0:
            data = {'Type':'Travel Time Collector', 'Name':'Empty', 'No':item[1], 'Time Travel Points':item[2], 'Display':('Travel Time Collector' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Travel Time Collector', 'Name':item[0], 'No':item[1],'Time Travel Points':item[2], 'Display':('Travel Time Collector' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)
    #print(dc_df)
    return dc_df

class Window(Frame): #similar a StartPage    
        
    def __init__(self, master): #master = parent class (BTC_app no exemplo. É none por que nao há classes superiores 'essa é só uma janela' )
        #print(type(master))
        Frame.__init__(self, master)
        
        container = tk.Frame(self)
        container.grid_rowconfigure(0, weight=1) 
        container.grid_columnconfigure(0, weight=1)
        
        self.dc_data = generate_dcdf()
        self.parameter_data = pd.DataFrame(columns = {'Experiment', 'Parameter', 'Lim. Inf', 'Lim. Sup', 'Step'})
        self.experiment_data = pd.DataFrame(columns = {'Experiment', 'Data Point Type', 'DP Number', 'Perf_measure', 'Time interval', 'Field data', 'Runs'}) 
        self.results_data = pd.DataFrame(columns = {'Experiment', 'Data Point Type', 'DP Number','Perf_measure','Time Interval','Run'})
        self.parameter_db = pd.read_csv(r'E:\Google Drive\Scripts\vistools\resources\parameters.visdb')
        self.master = master

        self.search_var = StringVar()
        
        self.switch = False
        self.search_mem = ''
        self.experiment = 1
        self.check_image = PhotoImage(file=r'E:\Google Drive\Scripts\vistools\resources\check.gif')
        
        self.collector_type = StringVar()
        self.collector_name = StringVar()
        self.collector_no = StringVar()
        self.collector_pm = StringVar()
        self.collector_timeinterval = StringVar()

        self.fake_data_data = {'Experiment': [1,1,1,2,2], 'Parameter': ['W74ax', 'W74bxAdd', 'W74bxMult','W74bxAdd', 'W74bxMult'], 'Lim. Inf': [1,1,1,2,2], 'Lim. Sup': [2,2,2,3,3], 'Step': [1, 1, 1, 1, 1]}
        self.fake_data = pd.DataFrame(self.fake_data_data, columns = ['Experiment', 'Parameter', 'Lim. Inf', 'Lim. Sup', 'Step'])

        fake_dc_data_data = {'Experiment': [1,1,1], 'Data Point Type': ['Data Collector', 'Travel Time Collector', 'Queue Counter'], 'DP Number': [6,3,1], 'Perf_measure': ['SpeedAvgArith','VehDelay','QLen'], 'Time Interval': ['Avg','Avg','Avg'], 'Field data': ['30','3.2','10']}
        self.fake_dc_data = pd.DataFrame(fake_dc_data_data, columns = ['Experiment', 'Data Point Type', 'DP Number', 'Perf_measure', 'Time Interval', 'Field data']) 

        self.results_data = pd.DataFrame(columns = {'Experiment', 'Data Point Type', 'DP Number','Perf_measure','Time Interval','Run','Read data'})
        
        self.grid(row=0, column=0)

        self.init_window()
        
       
    def init_window(self):  #TODO mudar para "experiment window"      
        
        self.master.title("Vistools")
        self.experiment_data_init = {'Experiment': 1} #TODO criar objeto "experiment"
        self.experiment_data = self.experiment_data.append(self.experiment_data_init, ignore_index=True)
        self.parameter_data = self.parameter_data.append(self.experiment_data_init, ignore_index=True)
        #print(self.experiment_data)
        #quitButton = Button(self, text = "Quit", command=self.client_exit)
        
        #quitButton.place(x=245, y=170)
        
        menu = Menu(self.master)
        self.master.config(menu=menu)
        
        file = Menu(menu)
        
        file.add_command(label = 'Exit', command = self.client_exit)
        
        menu.add_cascade(label="File", menu=file)
        
        edit = Menu(menu)     
                
        edit.add_command(label = 'Undo', command = lambda:popupmsg("wow! such programmin'"))
        
        #TODO adicionar botao para passar pra pagina de results

        menu.add_cascade(label='Edit', menu=edit)

         ##------Experiments section------##
        self.experiment_text = str('Experiment %i' % self.experiment)
        self.experiment_label = Label(self,text = self.experiment_text)
        
         ##------Datapoints section------##
        self.datapoints_label = Label(self,text = 'Data Points')
        self.datapoints_ctype_dropdown = ttk.Combobox(self, width=25)
        self.datapoints_ctype_dropdown['values'] = list(self.dc_data['Display'])
        self.datapoints_ctype_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctype_dropdown.set('Select data collector type')
        self.datapoints_ctype_dropdown.bind('<<ComboboxSelected>>', self.datapoints_callback)

        self.separator = ttk.Separator(self, orient="vertical")

        self.datapoints_cperfmeasure_dropdown = ttk.Combobox(self, width=25)
        self.datapoints_cperfmeasure_dropdown['values'] = []
        self.datapoints_cperfmeasure_dropdown.configure(font=('Roboto', 8))
        self.datapoints_cperfmeasure_dropdown.set('Select what you will measure')
        self.datapoints_cperfmeasure_dropdown.bind('<<ComboboxSelected>>', self.datapoints_callback)

        self.datapoints_ctimeinterval_label = Label(self, text='Add time interval number or agregation \n eg: 1,2,3,avg,min,max')
        self.datapoints_ctimeinterval_entry = Entry(self)

        self.datapoints_ctargetvalue_label=Label(self, text='Add the field data to compare')
        self.datapoints_ctargetvalue_entry=Entry(self)

        self.datapoint_ok_button = Button(self, command = self.button_callback, image=self.check_image)

        ##------Parameters section------##   
        self.parameters_label = Label(self,text = 'Parameters')      
        self.parameter_search_entry = Entry(self, textvariable=self.search_var, width=25)
        self.parameter_search_entry.insert(0, 'Search parameters here')
        self.parameter_search_listbox = Listbox(self, width=45, height=1)
        self.parameter_search_listbox.bind('<<ListboxSelect>>', self.parameters_callback)

        self.parameter_label_liminf = Label(self, text = 'Inferior Limit')
        self.parameter_entry_liminf = Entry(self, width=10)
        self.parameter_entry_liminf.bind('<FocusOut>', self.parameters_callback)

        self.parameter_label_limsup = Label(self, text = 'Superior Limit')
        self.parameter_entry_limsup = Entry(self, width=10)
        self.parameter_entry_limsup.bind('<FocusOut>', self.parameters_callback)

        self.parameter_label_step = Label(self, text = 'Step')
        self.parameter_entry_step = Entry(self, width=10)
        self.parameter_entry_step.bind('<FocusOut>', self.parameters_callback)

        ##------Simulation section------##
        self.simulation_label = Label(self, text = 'Simulation Configs')

        self.simulation_label_replications = Label(self, text = 'How many runs?')
        self.simulation_entry_replications = Entry(self, width=5)

        self.test_button =  Button(self, command = self.test_buttom, image=self.check_image)

        ##------Grid configuration------##
        self.experiment_label.grid(row=1, column=0, sticky=W)
        
        self.datapoints_label.grid(row=2, column=0, sticky=W, padx=10)
        self.datapoints_ctype_dropdown.grid(row=4, column=0, sticky=W, padx=10)
        self.datapoints_cperfmeasure_dropdown.grid(row=4, column=1, sticky=W, padx=10)
        self.datapoints_ctimeinterval_label.grid(row=3, column=2, sticky=W, padx=10)
        self.datapoints_ctimeinterval_entry.grid(row=4, column=2, sticky=W, padx=10)
        self.datapoints_ctargetvalue_label.grid(row=3, column=3, sticky=W, padx=10)
        self.datapoints_ctargetvalue_entry.grid(row=4, column=3, sticky=W, padx=10)
        self.datapoint_ok_button.grid(row=4, column=4, sticky=W, padx=10)
        
        self.separator.grid(row=2, column=5, sticky='ns', rowspan=100)

        self.parameters_label.grid(row=2, column=6, sticky=W, padx = 5)
        self.parameter_search_entry.grid(row=3, column=6, sticky =W, padx = 5)
        self.parameter_search_listbox.grid(row=4, column=6, sticky=W, padx = 5)
        self.parameter_label_liminf.grid(row=3, column=7, sticky=W, padx=5)
        self.parameter_entry_liminf.grid(row=4, column=7, sticky=W, padx=5)
        self.parameter_label_limsup.grid(row=3, column=8, sticky=W, padx=5)
        self.parameter_entry_limsup.grid(row=4, column=8, sticky=W, padx=5)
        self.parameter_label_step.grid(row=3, column=9, sticky=W, padx=5)
        self.parameter_entry_step.grid(row=4, column=9, sticky=W, padx=5)

        self.simulation_label.grid(row=5,column=0)
        self.simulation_label_replications.grid(row=6,column=0)
        self.simulation_entry_replications.grid(row=6,column=1)

        self.test_button.grid(row=9, column=5)
        
        #Function for updating the list/doing the search.
        #It needs to be called here to populate the listbox.
        self.update_list()

        self.poll()
    
    def button_callback(self):
        
        ctarget_entry = self.datapoints_ctargetvalue_entry.get()
        ctimeinterval_entry = self.datapoints_ctimeinterval_entry.get()
        simruns_entry = self.simulation_entry_replications.get()
        experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
        self.experiment_data.loc[experiment_index, 'Field data'] = ctarget_entry
        self.experiment_data.loc[experiment_index, 'Time interval'] = ctimeinterval_entry
        self.experiment_data.loc[experiment_index, 'Runs'] = simruns_entry

        
        #print(self.experiment_data)
    
    def test_buttom(self):

        self.vissim_simulation(experiment=1)

    def parameters_callback(self, eventObject):
        #print(eventObject.widget)

        # you can also get the value off the eventObject
        caller = str(eventObject.widget)
        parameter_index  = self.parameter_data.loc[self.parameter_data['Experiment']==self.experiment].index[0]

        if 'listbox' in caller:
            selected = self.parameter_search_listbox.curselection()
            parameter_text = self.parameter_search_listbox.get(first=selected, last=None)

            parameter_identifier_row = self.parameter_db.loc[self.parameter_db['Long Name']==parameter_text]
            
            value = str(parameter_identifier_row['Identifier'].item())
            
            #print(value)          

            self.parameter_data.loc[parameter_index, 'Parameter'] = value

            print(self.parameter_data)

        else:
            value = eventObject.widget.get()        

        if 'entry4' in caller: #liminf          
            self.parameter_data.loc[parameter_index, 'Lim. Inf'] = value
            print(self.parameter_data)
    
        elif 'entry5' in caller: #limsup  
            self.parameter_data.loc[parameter_index, 'Lim. Sup'] = value
            print(self.parameter_data)

        elif 'entry6' in caller: #step
            self.parameter_data.loc[parameter_index, 'Step'] = value
            print(self.parameter_data)
        
        else:
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            dc_match = self.dc_data.loc[self.dc_data['Display'] == value]
            data_point_type = dc_match['Type'].item()
            Dc_Number = dc_match['No'].item()

            self.experiment_data.loc[experiment_index, 'Data Point Type'] = data_point_type
            self.experiment_data.loc[experiment_index, 'DP Number'] = Dc_Number
            print(self.experiment_data)
          
        #print(self.experiment_data)
        
    def datapoints_callback(self, eventObject):
        # you can also get the value off the eventObject
        caller = str(eventObject.widget)
        value = eventObject.widget.get()

        if caller == None:
            entry_value = self.datapoints_ctargetvalue_entry.get()
            print(entry_value)
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            self.experiment_data.loc[experiment_index, 'Field data'] = entry_value
            print(self.experiment_data)
    
        elif 'combobox2' in caller:  
            print('selected1')       
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            self.experiment_data.loc[experiment_index, 'Perf_measure'] = value
            print(self.experiment_data)

        elif 'combobox3' in caller:
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            self.experiment_data.loc[experiment_index, 'Time interval'] = value
            print(self.experiment_data)

        else:
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            dc_match = self.dc_data.loc[self.dc_data['Display'] == value]
            data_point_type = dc_match['Type'].item()
            Dc_Number = dc_match['No'].item()         
            
            self.experiment_data.loc[experiment_index, 'Data Point Type'] = data_point_type
            self.experiment_data.loc[experiment_index, 'DP Number'] = Dc_Number

            if data_point_type == 'Data Collector':
                self.datapoints_cperfmeasure_dropdown['values'] = ['QueueDelay', 'SpeedAvgArith', 'OccupRate','Acceleration', 'Lenght', 'Vehs', 'Pers','Saturation Headway']

            elif data_point_type == 'Travel Time Collector':
                self.datapoints_cperfmeasure_dropdown['values'] = ['StopDelay', 'Stops', 'VehDelay', 'Vehs', 'Persons Delay', 'Persons']
                
            else:
                self.datapoints_cperfmeasure_dropdown['values'] = ['QLen', 'QLenMax', 'QStops']

            print(self.experiment_data)
           
        #print(self.experiment_data)

    def client_exit(self):
        root.destroy()
        print("oi")

    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        self._geom=geom
        print(geom, self._geom)
        self.master.geometry(self._geom)
           
    #Runs every 50 milliseconds. 
    def poll(self):
        #Get value of the entry box
        self.search = self.search_var.get()
        if self.search != self.search_mem: #self.search_mem = '' at start of program.
            self.update_list(is_contact_search=True)
            #set switch and search memory
            self.switch = True #self.switch = False at start of program.
            self.search_mem = self.search

        #if self.search returns to '' after preforming search 
        #it needs to reset the contents of the list box. I use 
        #a 'switch' to determine when it needs to be updated.
        if self.switch == True and self.search == '':
            self.update_list()
            self.switch = False
        self.after(50, self.poll)

    def update_list(self, **kwargs):
        try:
            is_contact_search = kwargs['is_contact_search']
        except:
            is_contact_search = False

        #Just a generic list to populate the listbox
                
        lbox_list = list(self.parameter_db['Long Name'])
        #print(lbox_list)

        self.parameter_search_listbox.delete(0, tk.END)

        for item in lbox_list:
            if is_contact_search == True:
                #Searches contents of lbox_list and only inserts
                #the item to the list if it self.search is in 
                #the current item.
                if self.search.lower() in item.lower():
                    self.parameter_search_listbox.insert(tk.END, item)
            else:
                self.parameter_search_listbox.insert(tk.END, item)

    def vissim_simulation(self, experiment):
        #This function sets up an runs the simulation for the selected experiment
        #runs = int(self.experiment_data.loc[self.experiment_data['Experiment']==experiment]['Runs'])
        runs = 2
        seed = 42
        Vissim.Simulation.SetAttValue('RandSeed', seed)

        #Filtering parameter and data points meta data
        selected_parameters = self.fake_data.loc[self.fake_data.Experiment == experiment] #temporary test experiment cfg
        #selected_datapts = self.fake_dc_data.loc[self.fake_dc_data.Experiment == experiment] #temporary test experiment cfg

        #print(selected_parameters)

        raw_possibilities = {}

        for index, item in self.fake_data.iterrows(): #gets the parameter data for the selected experiment
            
            #print(item)
            
            parameter = item['Parameter']
            inf = item['Lim. Inf']
            sup = item['Lim. Sup']
            step = item['Step']
            
            if type(inf) == type(sup) == int or type(inf) == type(sup) == float: #verifies if the parameter is a int/float type or str/bool
                #print(type(inf))                                                #and processes accordingly
                total_values = np.arange(inf, sup+step, step)
                
            else:
                #print(inf)
                total_values = [inf, sup]
                
            #print(total_values)
            
            raw_possibilities[parameter] = total_values #stores all the parameters values to be used later

        #print(raw_possibilities)
        allNames = sorted(raw_possibilities)
        combinations = list(it.product(*(raw_possibilities[Name] for Name in allNames))) #generates a list with all possible permutations
        #print(combinations)                                                             #of parameters
        #print(list(df.Parameter))

        self.selected_parameters = list(selected_parameters.Parameter)  #stores the parameter's names
        parameters_df = pd.DataFrame(combinations, columns=self.selected_parameters) #organizes all runs cfg data

        #------------------------------------#
                
        for index, parameter_data in parameters_df.iterrows():
            #print(parameter_data)

            parameter_names = list(parameters_df)

            for i in range(len(parameter_names)):

                parameter_name = str(parameter_names[i])
                parameter_data_ = int(parameter_data[i])

                Vissim.Net.DrivingBehaviors[0].SetAttValue(parameter_name,parameter_data_)
                #Vissim.Net.DrivingBehaviors[0].SetAttValue('W74ax',1)
                
            for run in range(runs):
                seed += 1
                Vissim.Simulation.SetAttValue('RandSeed', seed)

                Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
                
                Vissim.Simulation.RunContinuous() #Iniciando Simulação 

                for index, dc_data in self.fake_dc_data.iterrows():

                    if dc_data['Data Point Type'] == 'Data Collector':

                        if dc_data['Perf_measure'] == 'Saturation Headway':
                            
                            headways = calculate_shdwy(path_network, dc_data['DP Number'].item) #TODO Como lidar com as varias replicacoes?
                            
                        else:
                            selected_dc = Vissim.Net.DataCollectionMeasurements.ItemByKey(int(dc_data['DP Number']))
                            result = selected_dc.AttValue('{}(Current,{},All)'.format(str(dc_data['Perf_measure']), str(dc_data['Time Interval'])))

                        
                    elif dc_data['Data Point Type'] == 'Travel Time Collector':
                        
                        selected_ttc = Vissim.Net.DelayMeasurements.ItemByKey(int(dc_data['DP Number']))
                        result = selected_ttc.AttValue('{}(Current,{},All)'.format(str(dc_data['Perf_measure']), str(dc_data['Time Interval'])))
                                                    
                    else:
                        selected_qc = Vissim.Net.QueueCounters.ItemByKey(int(dc_data['DP Number']))
                        result = selected_qc.AttValue('{}(Current,{})'.format(str(dc_data['Perf_measure']), str(dc_data['Time Interval'])))
                        
                    results = {'Experiment':1, 'Data Point Type':str(dc_data['Data Point Type']), 'DP Number':str(dc_data['DP Number']),'Perf_measure':str(dc_data['Perf_measure']),
                            'Time Interval':str(dc_data['Time Interval']),'Run':str(run),'Read data':str(result)}

                    self.results_data = self.results_data.append(results, ignore_index=True) #TODO Formatar para exportar pra dashboard

        self.results_data.to_csv(r"E:\Google Drive\Scripts\vistools\output.csv", sep = ';')

#TODO Adicionar a pagina dos resultados                    




                    




root = Tk()
root.geometry("1920x1080")
#root.state('zoomed')
app = Window(master = root)
root.mainloop()
