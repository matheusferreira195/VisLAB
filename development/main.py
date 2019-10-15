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
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import sqlite3

#Database connection
cnx = sqlite3.connect(r'C:\Users\mathe\Desktop\vislab.db')

#Setting up FONTS
NORM_FONT= ("Roboto", 10)
LARGE_FONT = ("Roboto", 20)

#Main app class
class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    #function to swap pages to front
    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    
    #Page that has infos and tutorials

    def __init__(self, parent, controller):

        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = tk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = tk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()
    
class PageOne(tk.Frame):

    #Experiment page, where the user models the sensitivity analysis experiments

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.grid(row=0,column=0)
        
        ##Navigation controls
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0,column=1)

        button2 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.grid(row=0,column=2)
        
        #storage initialization #FIXME is really necessary?

        #self.parameter_data = pd.DataFrame(columns = {'Experiment', 'Parameter', 'Lim. Inf', 'Lim. Sup', 'Step'})
        #self.experiment_data = pd.DataFrame(columns = {'Experiment', 'Data Point Type', 'DP Number', 'Perf_measure', 'Time interval', 'Field data', 'Runs'}) 
        #self.results_data = pd.DataFrame(columns = {'Experiment', 'Data Point Type', 'DP Number','Perf_measure','Time Interval','Run'})
        #self.parameter_db = pd.read_csv(r'E:\Google Drive\Scripts\vistools\resources\parameters.visdb')

        #variable initialization
        
        self.search_var = tk.StringVar()
        
        self.switch = False
        self.search_mem = ''
        self.experiment = 1
        self.check_image = tk.PhotoImage(file=r'E:\Google Drive\Scripts\vistools\resources\check.gif')
        
        self.collector_type = tk.StringVar()
        self.collector_name = tk.StringVar()
        self.collector_no = tk.StringVar()
        self.collector_pm = tk.StringVar()
        self.collector_timeinterval = tk.StringVar()

        self.fake_data_data = {'Experiment': [1,1,1,2,2], 'Parameter': ['W74ax', 'W74bxAdd', 'W74bxMult','W74bxAdd', 'W74bxMult'], 'Lim. Inf': [1,1,1,2,2], 'Lim. Sup': [2,2,2,3,3], 'Step': [1, 1, 1, 1, 1]}
        self.fake_data = pd.DataFrame(self.fake_data_data, columns = ['Experiment', 'Parameter', 'Lim. Inf', 'Lim. Sup', 'Step'])

        fake_dc_data_data = {'Experiment': [1,1,1], 'Data Point Type': ['Data Collector', 'Travel Time Collector', 'Queue Counter'], 'DP Number': [6,3,1], 'Perf_measure': ['SpeedAvgArith','VehDelay','QLen'], 'Time Interval': ['Avg','Avg','Avg'], 'Field data': ['30','3.2','10']}
        self.fake_dc_data = pd.DataFrame(fake_dc_data_data, columns = ['Experiment', 'Data Point Type', 'DP Number', 'Perf_measure', 'Time Interval', 'Field data'])         
        self.grid(row=0, column=0)

        self.init_window()
        
       
    def init_window(self):  #TODO mudar para "experiment window" 
       # self.master.title("Vistools")
        self.experiment_data_init = {'Experiment': 1} #TODO criar objeto "experiment"
        self.experiment_data = self.experiment_data.append(self.experiment_data_init, ignore_index=True)
        self.parameter_data = self.parameter_data.append(self.experiment_data_init, ignore_index=True)
        #print(self.experiment_data)
        #quitButton = Button(self, text = "Quit", command=self.client_exit)
        
        #quitButton.place(x=245, y=170)

         ##------Experiments section------##
        self.experiment_text = str('Experiment %i' % self.experiment)
        self.experiment_label = tk.Label(self,text = self.experiment_text)

        ##------Datapoints section------##
        self.datapoints_label = tk.Label(self,text = 'Data Points')
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

        self.datapoints_ctimeinterval_label = tk.Label(self, text='Add time interval number or agregation \n eg: 1,2,3,avg,min,max')
        self.datapoints_ctimeinterval_entry = tk.Entry(self)

        self.datapoints_ctargetvalue_label=tk.Label(self, text='Add the field data to compare')
        self.datapoints_ctargetvalue_entry= tk.Entry(self)

        self.datapoint_ok_button = tk.Button(self, command = lambda: self.button_callback)# image=self.check_image)

        ##------Parameters section------##   
        self.parameters_label = tk.Label(self,text = 'Parameters')      
        self.parameter_search_entry = tk.Entry(self, textvariable=self.search_var, width=25)
        self.parameter_search_entry.insert(0, 'Search parameters here')
        self.parameter_search_listbox = tk.Listbox(self, width=45, height=1)
        self.parameter_search_listbox.bind('<<ListboxSelect>>', self.parameters_callback)

        self.parameter_label_liminf = tk.Label(self, text = 'Inferior Limit')
        self.parameter_entry_liminf = tk.Entry(self, width=10)
        self.parameter_entry_liminf.bind('<FocusOut>', self.parameters_callback)

        self.parameter_label_limsup = tk.Label(self, text = 'Superior Limit')
        self.parameter_entry_limsup = tk.Entry(self, width=10)
        self.parameter_entry_limsup.bind('<FocusOut>', self.parameters_callback)

        self.parameter_label_step = tk.Label(self, text = 'Step')
        self.parameter_entry_step = tk.Entry(self, width=10)
        self.parameter_entry_step.bind('<FocusOut>', self.parameters_callback)

        ##------Simulation section------##
        self.simulation_label = tk.Label(self, text = 'Simulation Configs')

        self.simulation_label_replications = tk.Label(self, text = 'How many runs?')
        self.simulation_entry_replications = tk.Entry(self, width=5)

        self.test_button = tk.Button(self, command = lambda: self.test_buttom)#, image=self.check_image)

        ##------Grid configuration------##
        self.experiment_label.grid(row=1, column=0, sticky='w')
        
        self.datapoints_label.grid(row=2, column=0, sticky='w', padx=10)
        self.datapoints_ctype_dropdown.grid(row=4, column=0, sticky='w', padx=10)
        self.datapoints_cperfmeasure_dropdown.grid(row=4, column=1, sticky='w', padx=10)
        self.datapoints_ctimeinterval_label.grid(row=3, column=2, sticky='w', padx=10)
        self.datapoints_ctimeinterval_entry.grid(row=4, column=2, sticky='w', padx=10)
        self.datapoints_ctargetvalue_label.grid(row=3, column=3, sticky='w', padx=10)
        self.datapoints_ctargetvalue_entry.grid(row=4, column=3, sticky='w', padx=10)
        self.datapoint_ok_button.grid(row=4, column=4, sticky='w', padx=10)
        
        self.separator.grid(row=2, column=5, sticky='ns', rowspan=100)

        self.parameters_label.grid(row=2, column=6, sticky='w', padx = 5)
        self.parameter_search_entry.grid(row=3, column=6, sticky ='w', padx = 5)
        self.parameter_search_listbox.grid(row=4, column=6, sticky='w', padx = 5)
        self.parameter_label_liminf.grid(row=3, column=7, sticky='w', padx=5)
        self.parameter_entry_liminf.grid(row=4, column=7, sticky='w', padx=5)
        self.parameter_label_limsup.grid(row=3, column=8, sticky='w', padx=5)
        self.parameter_entry_limsup.grid(row=4, column=8, sticky='w', padx=5)
        self.parameter_label_step.grid(row=3, column=9, sticky='w', padx=5)
        self.parameter_entry_step.grid(row=4, column=9, sticky='w', padx=5)

        self.simulation_label.grid(row=5,column=0)
        self.simulation_label_replications.grid(row=6,column=0)
        self.simulation_entry_replications.grid(row=6,column=1)

        self.test_button.grid(row=9, column=5)
        
        #Function for updating the list/doing the search.
        #It needs to be called here to populate the listbox

        self.update_list()
        self.poll()

    def button_callback(self):

        print('pressde')
        ctarget_entry = self.datapoints_ctargetvalue_entry.get()
        ctimeinterval_entry = self.datapoints_ctimeinterval_entry.get()
        simruns_entry = self.simulation_entry_replications.get()
        experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
        self.experiment_data.loc[experiment_index, 'Field data'] = ctarget_entry
        self.experiment_data.loc[experiment_index, 'Time interval'] = ctimeinterval_entry
        self.experiment_data.loc[experiment_index, 'Runs'] = simruns_entry

        print(self.experiment_data)
    
    def test_buttom(self):

        self.vissim_simulation(experiment=1)

    def parameters_callback(self, eventObject):
        #print(eventObject.widget)

        # you can also get the value off the eventObject
        caller = str(eventObject.widget)
        parameter_index  = self.parameter_data.loc[self.parameter_data['Experiment']==self.experiment].index[0]
        #print(parameter_index)
        #print(self.parameter_data)

        if 'listbox' in caller:
            #print(self.parameter_search_listbox)
            selected = self.parameter_search_listbox.curselection()
            parameter_text = self.parameter_search_listbox.get(first=selected, last=None)

            parameter_identifier_row = self.parameter_db.loc[self.parameter_db['Long Name']==parameter_text]
            
            value = str(parameter_identifier_row['Identifier'].item())
            
            #print(value)          

            self.parameter_data.loc[parameter_index, 'Parameter'] = value

            #print(self.parameter_data)

        else:

            value = eventObject.widget.get()        

        if 'entry4' in caller: #liminf          
            self.parameter_data.loc[parameter_index, 'Lim. Inf'] = value
            #print(self.parameter_data)
    
        elif 'entry5' in caller: #limsup  
            self.parameter_data.loc[parameter_index, 'Lim. Sup'] = value
            #print(self.parameter_data)

        elif 'entry6' in caller: #step
            self.parameter_data.loc[parameter_index, 'Step'] = value
           # print(self.parameter_data)
        
        else:
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            dc_match = self.dc_data.loc[self.dc_data['Display'] == value]
            data_point_type = dc_match['Type'].item()
            Dc_Number = dc_match['No'].item()

            self.experiment_data.loc[experiment_index, 'Data Point Type'] = data_point_type
            self.experiment_data.loc[experiment_index, 'DP Number'] = Dc_Number
            #print(self.experiment_data)
        
        #print(self.experiment_data)
        
    def datapoints_callback(self, eventObject):
        # you can also get the value off the eventObject
        caller = str(eventObject.widget)
        value = eventObject.widget.get()

        if caller == None:
            entry_value = self.datapoints_ctargetvalue_entry.get()
            #print(entry_value)
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
            print(self.experiment_data)
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
        #print(self.search)
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
        Vissim.Simulation.SetAttValue('NumRuns', runs)

        #Filtering parameter and data points meta data
        selected_parameters = self.fake_data.loc[self.fake_data.Experiment == experiment] #temporary test experiment cfg
        selected_datapts = self.fake_dc_data.loc[self.fake_dc_data.Experiment == experiment] #temporary test experiment cfg

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
        self.parameters_df = pd.DataFrame(combinations, columns=self.selected_parameters) #organizes all runs cfg data
        #print(parameters_df)
        #------------------------------------#
                
        for index_par, parameter_data in self.parameters_df.iterrows():
            #print(parameter_data)

            parameter_names = list(self.parameters_df)

            #Configures the simulation
            for i in range(len(parameter_names)):

                    parameter_name = str(parameter_names[i])
                    parameter_data_ = int(parameter_data[i])

                    Vissim.Net.DrivingBehaviors[0].SetAttValue(parameter_name,parameter_data_)
                    #Vissim.Net.DrivingBehaviors[0].SetAttValue('W74ax',1)
                
            
            Vissim.Simulation.SetAttValue('RandSeed', seed)

            Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
            
            Vissim.Simulation.RunContinuous() #Iniciando Simulação 

            for index, dc_data in selected_datapts.iterrows(): #Collects perf_measure data #FIXME Trocar pra pegar os dc_data filtrados por experiemnto
                
                for replication in range(1,runs+1):

                    if dc_data['Data Point Type'] == 'Data Collector':
    
                        if dc_data['Perf_measure'] == 'Saturation Headway':
                            print('problema')
                            #A função ja tem replication handling
                            result = calculate_shdwy(path_network, dc_data['DP Number'].item, replication) 
                            
                        else:
    
                            selected_dc = Vissim.Net.DataCollectionMeasurements.ItemByKey(int(dc_data['DP Number'])) 
                            result = selected_dc.AttValue('{}({},{},All)'.format(str(dc_data['Perf_measure']), 
                                                        str(replication), 
                                                        str(dc_data['Time Interval'])))
    
                        
                    elif dc_data['Data Point Type'] == 'Travel Time Collector':
    
                        
                        selected_ttc = Vissim.Net.DelayMeasurements.ItemByKey(int(dc_data['DP Number']))
                        result = selected_ttc.AttValue('{}({},{},All)'.format(str(dc_data['Perf_measure']), 
                                                    str(replication), 
                                                    str(dc_data['Time Interval'])))
                                                    
                    else:    
                        
                        selected_qc = Vissim.Net.QueueCounters.ItemByKey(int(dc_data['DP Number']))
                        result = selected_qc.AttValue('{}({},{})'.format(str(dc_data['Perf_measure']), 
                                                    str(replication), 
                                                    str(dc_data['Time Interval'])))
                        
                    results = {'Experiment':1, 
                            'Data Point Type':str(dc_data['Data Point Type']), 
                            'DP Number':str(dc_data['DP Number']),
                            'Perf_measure':str(dc_data['Perf_measure']),
                            'Time Interval':str(dc_data['Time Interval']),
                            'Run':str(replication),
                            'Read data':str(result),
                            'Parameters':str(index_par)}
    
                    self.results_data = self.results_data.append(results, ignore_index=True) #TODO Formatar para exportar pra dashboard

        self.results_data.to_csv(r"E:\Google Drive\Scripts\vistools\output.csv", sep = ';')


#TODO Adicionar a pagina dos resultados                    
class PageTwo(PageOne):

    def __init__(self, parent, controller):
        PageOne.__init__(self, parent, controller)
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.grid(row=0,column=0)

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0,column=1)

        button2 = tk.Button(self, text="Page One",
                            command=lambda: controller.show_frame(PageOne))
        button2.grid(row=0,column=2)

        #Section 1: graphs related to single parameter analysis

        label_s1 = tk.Label(self, text = "Single Parameter analysis")
        label_s1.grid(row=1,column=0)

        plot_cfgs = []
        #label_expselect = tk.Label(self, text="")

        self.exp_select = ttk.Combobox(self, width=25)
        self.exp_select['values'] = list(set(self.experiment_data['Experiment']))
        self.exp_select.configure(font=('Roboto', 8))
        self.exp_select.set('Select the Experiment')
        self.exp_select.bind('<<ComboboxSelected>>', self.plot_cfg)
        self.exp_select.grid(row=2, column=0)

        self.p1 = ttk.Combobox(self, width=25)
        self.p1['values'] = list(set(self.parameter_data['Parameter']))
        self.p1.configure(font=('Roboto', 8))
        self.p1.set('Select the Parameter')
        self.p1.bind('<<ComboboxSelected>>', self.plot_cfg)
        self.p1.grid(row=3, column=0)

        self.p2 = ttk.Combobox(self, width=25)
        self.p2['values'] = list(set(self.parameter_data['Parameter']))
        self.p2.configure(font=('Roboto', 8))
        self.p2.set('Select the Perf. Measure')
        self.p2.bind('<<ComboboxSelected>>', self.plot_cfg)
        self.p2.grid(row=4, column=0)

        self.titles_lbl = tk.Label(self, text="Altere o título aqui")#TODO adicionar label e entry para pegar o titulo que o cara quiser colocar
        self.titles_lbl.grid(row=5,column=0)
        self.titles = tk.Entry(self)
        self.titles.grid(row=5,column=1)
        
        self.f = Figure(figsize=(5,5), dpi=100)

        self.testbutton = tk.Button(self, command=lambda: self.plots_single('W74ax','SpeedAvgArith',1,None,1))
        self.testbutton.grid(row=6,column=1)

    def plot_cfg(self, eventObject):

        caller = str(eventObject.widget)
        value = eventObject.widget.get()
        print(caller)
        print(value)  


    def plots_single(self, parameter, perf_measure, p_type, title, experiment, *kwargs):
        
        #getting the parameters and results data by selected experiment
        parameters_df_by_experiment = parameters_df.loc[parameters_df['Experiment']==experiment]
        #print(self.results_data)
        data_by_experiment = teste_results.loc[teste_results['Experiment']==experiment]
        print(data_by_experiment)
        #getting the data of the max/min parameter value
        parameter_min = self.parameters_df[parameter].idxmin()
        parameter_max = self.parameters_df[parameter].idxmax()
        
        #if the graph is a scatterplot
        if p_type == 0:        
        
            results_min = list(data_by_experiment.loc[(data_by_experiment['Parameters']==parameter_min) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data'])
            results_max = list(data_by_experiment.loc[(data_by_experiment['Parameters']==parameter_max) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data'])
            
            print(results_min)
            print(results_max)
            
            matplotlib.scatter(results_min, results_max, color='g')
            matplotlib.xlabel(perf_measure + ' Min.')
            matplotlib.ylabel(perf_measure + ' Máx.')
            matplotlib.title(parameter)
            matplotlib.show()
        
        #if the graph is a line chart, by runs
        if p_type == 1:
            
            results_min = np.asarray(list(data_by_experiment.loc[(data['Parameters']==parameter_min) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data']))
            results_max = np.asarray(list(data_by_experiment.loc[(data['Parameters']==parameter_max) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data']))
            
            print(results_min)
            print(results_max)
            
            rep = np.asarray(list(set(list(data_by_experiment['Run'].loc[data_by_experiment['Parameters']==parameter_min]))))
            
            print(rep)
            #results_min = [1,2]
            #results_max = [3,4]
            #rep = [9,8]
            a = self.f.add_subplot(111)
            a.plot(rep, results_min, color='green')
            a.plot(rep, results_max, color='blue')
            a.xlabel(perf_measure)
            a.ylabel('# Simulations')
            a.xticks(rep)
            a.title(parameter)
            #matplotlib.show()
            canvas = FigureCanvasTkAgg(self.f, self)
            canvas.show()
            canvas.get_tk_widget().grid(row=3, column=4)



    def plot_multi(self, experiment, g_type):         #TODO Adicionar a funcao para gerar a matriz de correlacao
        
        #if g_type == 'boxplot':


        

        None

app = SeaofBTCapp()
app.mainloop()