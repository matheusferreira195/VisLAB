# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:05:28 2019

@author: mathe
"""
import tkinter as tk
import sqlite3
import pandas as pd
import math
from scipy import stats
from tkinter import ttk
from tkinter import messagebox
from generate_dcdf import generate_dcdf
from generate_dcdf import generate_dcdf_test
from functools import partial
import numpy as np
import itertools as it
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from itertools import groupby
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization! 
from os import listdir
from os.path import isfile, join
import glob
import os
import win32com.client as com

#loading assets
NORM_FONT= ("Roboto", 10)
LARGE_FONT = ("Roboto", 20)


#Database connection and set up

cnx = sqlite3.connect(r'E:\Google Drive\Scripts\VisLab\resources\vislab.db')#, isolation_level=None)
gaCnx = sqlite3.connect(r'E:\Google Drive\Scripts\VisLab\resources\ga.db')
sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))
cursor = cnx.cursor()

def formatting(tipe, path):
    skipline = 0
    
    if tipe == '.mer':
        keyword = ' Measurem.'
        
    elif tipe == '.lsa':
        keyword = 'SC'
    
    with open(path) as f:
        
        lines = f.readlines()
        
        for chunk in enumerate(lines):
            if keyword in chunk[1]:
                
                if tipe == '.lsa':
                
                    skipline = int(chunk[0] + 2)
                    
                else:
                    skipline = int(chunk[0])
        #print(skipline)    
        return skipline
    

def calculate_shdwy(path, dc, replication):
    lsa_columns = ['SimSec', 'CycleSec', 'SC', 'SG', 'Aspect', 'Prev', 'Crit', 'duetoSG']
    os.chdir(path)
    mers = [file for file in glob.glob("*.mer")]
    lsas = [file for file in glob.glob("*.lsa")]
    headways_df = pd.DataFrame(columns=['Replication','Cicle','Position','Headway'])
    #print(mers)
    #print(len(mers))
    for i in range(len(mers)):


        mer_data_raw = pd.read_csv(mers[i], sep=';', skiprows=formatting('.mer',mers[i]), skipinitialspace=True, index_col=False) 
        mer_data = mer_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        #print(mer_data_raw)
        lsa_data_raw = pd.read_csv(lsas[i], sep=';', skiprows=formatting('.lsa',lsas[i]), names=lsa_columns, skipinitialspace=True, index_col=False)
        lsa_data = lsa_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        #print(lsa_data_raw)
        green_windows = lsa_data[(lsa_data['Aspect'] == 'green') & (lsa_data['Aspect']=='red')]['SimSec']
        raw_green_windows = lsa_data.query('Aspect in list(["green", "red"])').reset_index(drop=True)

        cleaned_mer = mer_data[(mer_data['t(Entry)'] !=0 )]     
        
        green_windows=[]
        interval=[]
        
        for w in range(len(raw_green_windows['SimSec']) -1):

            if raw_green_windows['Aspect'][w] == 'green':
                    
                interval = [raw_green_windows['SimSec'][w],raw_green_windows['SimSec'][w+1]]    
                green_windows.append(interval)
        
        for j in range(len(green_windows)):
            
            headways_to_bar = []

            
            df = cleaned_mer[(cleaned_mer['t(Entry)'] > green_windows[j][0]) 
                            & (cleaned_mer['t(Entry)'] < green_windows[j][1]) 
                            & (cleaned_mer['tQueue'] != 0)
                            & (cleaned_mer['Measurem.'] == dc)]
            
            if not df.empty:
                
                
                filtrados = list(df['t(Entry)'])

                if len(filtrados) >= 4:

                    for k in range(1,len(filtrados)):
                        
                        headway = filtrados[k] - filtrados[k-1]
                        headways_dict = {'Replication':i+1,'Cicle':green_windows[j],'Position':k, 'Headway': headway}
                        headways_to_bar.append(headway)
                        
                        headways_df = headways_df.append(headways_dict, ignore_index = True)
                        headways_df = headways_df[headways_df['Replication'] == replication]
                        headway_mean = headways_df[headways_df['Position'] == 4]['Headway'].mean()
                
    return headway_mean 
    
        
def vissim_simulation(experiment,default = 0):

    '''Vissim = None #com.Dispatch('Vissim.Vissim')
    Vissim = com.Dispatch("Vissim.Vissim") #Abrindo o Vissim
    path_network =r'E:\Google Drive\Scripts\VisLab\development\net\teste\teste.inpx'
    flag = False 
    Vissim.LoadNet(path_network, flag) #Carregando o arquivo'''

    #Loading initial data sources
    simCfg = pd.read_sql(str('SELECT * FROM simulation_cfg WHERE experiment = %s' % experiment),cnx)
    selected_datapts = pd.read_sql(str('SELECT * FROM datapoints WHERE experiment = %s' % experiment),cnx) #self.datapoints_df.loc[self.datapoints_df['experiment']==experiment]
    selected_parameters = pd.read_sql(str('SELECT * FROM parameters WHERE experiment = %s' % experiment),cnx)#self.parameters_df.loc[self.parameters_df['experiment']==experiment]
    #print('simCfg')
    #print(simCfg)

    #Loading some sim cfg parameters
    runs = int(simCfg['replications'][0])
    seed = int(simCfg['initial_seed'][0])
    seed_inc = int(simCfg['seed_increment'][0])
    
    if default == 1:

        #Runs the net with default parameter values 

        Vissim.Simulation.SetAttValue('RandSeed', seed)
        Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
        Vissim.Simulation.RunContinuous() #Iniciando Simulação 

        for index, dc_data in selected_datapts.iterrows(): #TODO testar se roda pros defaults
                
                for replication in range(1,runs+1):
                    
                    if dc_data['dc_type'] == 'Data Collector':

                        if dc_data['perf_measure'] == 'Saturation Headway':
                            print('problema')
                            result = calculate_shdwy(path_network, dc_data['dc_number'].item, replication) 
                            
                        else:
                            print(dc_data['time_p'])
                            selected_dc = Vissim.Net.DataCollectionMeasurements.ItemByKey(int(dc_data['dc_number'])) 
                            result = selected_dc.AttValue('{}({},{},All)'.format(str(dc_data['perf_measure']), 
                                                        str(replication), 
                                                        str(dc_data['time_p'])))

                    elif dc_data['dc_type'] == 'Travel Time Collector':

                        selected_ttc = Vissim.Net.DelayMeasurements.ItemByKey(int(dc_data['dc_number']))
                        result = selected_ttc.AttValue('{}({},{},All)'.format(str(dc_data['perf_measure']), 
                                                    str(replication), 
                                                    str(dc_data['time_p'])))
                                                    
                    else:    
                        
                        selected_qc = Vissim.Net.QueueCounters.ItemByKey(int(dc_data['dc_number']))
                        result = selected_qc.AttValue('{}({},{})'.format(str(dc_data['perf_measure']), 
                                                    str(replication), 
                                                    str(dc_data['time_p'])))
                    

                    for p_name,p_value in row.iteritems():

                        seedDb = seed + replication*seed_inc

                        cursor.execute("UPDATE simulation_runs SET results = %s WHERE experiment = %s AND parameter_name = '%s' AND parameter_value = %s AND seed = %s" % (result,experiment,'default','default',seedDb))
                        cnx.commit()
    else:

        #Vissim.Simulation.SetAttValue('RandSeed', seed)
        #Vissim.Simulation.SetAttValue('NumRuns', runs)

        raw_possibilities = {}

        for index, item in selected_parameters.iterrows(): #gets the parameter data for the selected experiment
            
            #print(item)
            
            parameter = item['parameter_name']
            inf = item['parameter_b_value']
            sup = item['parameter_u_value']
            step = item['parameter_step']
            
            if type(inf) == type(sup) == int or type(inf) == type(sup) == float: #verifies if the parameter is a int/float type or str/bool
                #print(type(inf))                                                #and processes accordingly
                total_values = np.arange(inf, sup+step, step)
                
            else:
                #print(inf)
                total_values = [inf, sup]
                
            #print(total_values)
            
            raw_possibilities[parameter] = total_values #stores all the parameters values to be used later

            
        allNames = sorted(raw_possibilities)
        combinations = list(it.product(*(raw_possibilities[Name] for Name in allNames))) #generates a list with all possible permutations
        #print(combinations)                                                             #of parameters
        #print(list(df.Parameter))
        
        selectedParameters = list(selected_parameters['parameter_name'])  #stores the parameter's names
        #print(selectedParameters)
        parameters_df = pd.DataFrame(combinations, columns=selectedParameters) #organizes all runs cfg data
        #print(parameters_df)

        #------------------------------------#
                
        for index, row in parameters_df.iterrows():
            print(index)
            print(row)
            parameter_names = list(parameters_df)
            #print(parameter_names)
            #print('parameter_names')
            #print(parameter_names)
            #Configures the simulation

            for i in range(len(parameter_names)): #loop that cfgs the simulation's parameters

                parameter_name = str(parameter_names[i])
                #print(parameter_name)
                parameter_df_ = int(row[i])
                #print(parameter_df_)
                #print(parameter_df_)        
                #print('%s = %s' % (parameter_name,str(parameter_df_)))

                for seed_m in range(1,runs+1): #just registers the simulations seed for later filling

                    seed_t = seed+seed_m*seed_inc
                    query = "INSERT INTO simulation_runs (experiment,parameter_name,parameter_value,seed,sim_perf) VALUES (%s,'%s',%s,%s,%s)" % (str(experiment),
                                                                                                                            str(parameter_name),
                                                                                                                            str(parameter_df_),
                                                                                                                            str(seed_t),str(index))
                    print(query)
                    cursor.execute(query)
                    cnx.commit() 

                #Vissim.Net.DrivingBehaviors[0].SetAttValue(parameter_name,parameter_df_)

            #Vissim.Simulation.SetAttValue('RandSeed', seed)
            #Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
            #Vissim.Simulation.RunContinuous() #Iniciando Simulação 

            '''for index, dc_data in selected_datapts.iterrows(): #Collects perf_measure data #FIXME Trocar pra pegar os dc_data filtrados por experiemnto
                
                for replication in range(1,runs+1):
                    
                    if dc_data['dc_type'] == 'Data Collector':

                        if dc_data['perf_measure'] == 'Saturation Headway':
                            print('problema')
                            #A função ja tem replication handling
                            result = calculate_shdwy(path_network, dc_data['dc_number'].item, replication) 
                            
                        else:
                            print(dc_data['time_p'])
                            selected_dc = Vissim.Net.DataCollectionMeasurements.ItemByKey(int(dc_data['dc_number'])) 
                            result = selected_dc.AttValue('{}({},{},All)'.format(str(dc_data['perf_measure']), 
                                                        str(replication), 
                                                        str(dc_data['time_p'])))

                    elif dc_data['dc_type'] == 'Travel Time Collector':

                        selected_ttc = Vissim.Net.DelayMeasurements.ItemByKey(int(dc_data['dc_number']))
                        result = selected_ttc.AttValue('{}({},{},All)'.format(str(dc_data['perf_measure']), 
                                                    str(replication), 
                                                    str(dc_data['time_p'])))
                                                    
                    else:    
                        
                        selected_qc = Vissim.Net.QueueCounters.ItemByKey(int(dc_data['dc_number']))
                        result = selected_qc.AttValue('{}({},{})'.format(str(dc_data['perf_measure']), 
                                                    str(replication), 
                                                    str(dc_data['time_p'])))
                    
                    print(row)
                    print('\n')

                    for p_name,p_value in row.iteritems():

                        seedDb = seed + replication*seed_inc

                        cursor.execute("UPDATE simulation_runs SET results = %s WHERE experiment = %s AND parameter_name = '%s' AND parameter_value = %s AND seed = %s" % (result,experiment,p_name,p_value,seedDb))
                        cnx.commit()
        Vissim = None '''  
 
class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid(row=0,column=0)

        self.frames = {}

        for F in (StartPage, Board, ResultsPage, CalibrationPage):

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
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.place(in_=self, anchor="c", relx=.5, rely=.5)

        self.calPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\ga.png")  #https://www.flaticon.com/packs/science-121
        self.saPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\sa.png")
        self.flaskPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\flask.png")
        label = tk.Label(frame, text="VisLab", font=LARGE_FONT)
        label.grid(row=0,column=1)
 
        button = tk.Button(frame, text="Experiment board",
                            command=lambda: controller.show_frame(Board),image=self.flaskPhoto)
        button.grid(row=1,column=0,pady=200)

        button2 = tk.Button(frame, text="Results Dashboard",
                            command=lambda: controller.show_frame(ResultsPage),image=self.saPhoto)
        button2.grid(row=1,column=1,pady=200)

        button2 = tk.Button(frame, text="Calibration",
                            command=lambda: controller.show_frame(CalibrationPage),image=self.calPhoto)
        button2.grid(row=1,column=2,pady=200)

dc_data = generate_dcdf_test()
parameter_db = pd.read_csv(r'E:\Google Drive\Scripts\VisLab\resources\parameters.visdb')       
class Board(tk.Frame):

    #Experiment page, where the user models the sensitivity analysis experiments
    #Now, it's also the 'sticker panel', where the user can manage the experiments like a post it board

    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Manage your experiments", font=LARGE_FONT)
        label.grid(row=0,column=0)
        
        #loading existing post its (experiments)

        existing_experiments_qry = "SELECT id FROM experiments"
        existing_experiments = pd.read_sql(existing_experiments_qry,cnx)

        self.datapoints_df = pd.read_sql(str('SELECT * FROM datapoints'), cnx)
        #print(self.datapoints_df)
        self.parameters_df = pd.read_sql(str('SELECT * FROM parameters'), cnx)
        self.simulation_runs = pd.read_sql(str('SELECT * FROM simulation_runs'), cnx)
        
        #print(existing_experiments[0])
        self.add_buttons = []        
        self.canvas_l = []
        #getting the stickers from previous section (experiments saved on the db)
        if len(existing_experiments.index) == 0:

            self.plus_button = tk.Button(self, text = '+', command=lambda:self.add_postit(1,0))
            self.plus_button.grid(row=1,column=1)

        for row in existing_experiments.iterrows():

                y = int(row[0])
                x = math.ceil((int(row[0])/4)+0.1)
                #print(x)
                self.add_postit(x,y,exp=int(row[1]),btn_id=row[0])
        
        #dynamic search bar init
        

        #Navigation

        button_back = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button_back.grid(row=0,column=1)
        
        button_calibration = tk.Button(self, text="Calibration",
                            command=lambda: controller.show_frame(PageTwo))
        button_calibration.grid(row=0,column=2)
        
        button_signal = tk.Button(self, text="Signal Calibration",
                            command=lambda: controller.show_frame(PageTwo))
        button_signal.grid(row=0,column=3)

        button_results = tk.Button(self, text="Results Dashboard",
                       command=lambda: controller.show_frame(ResultsPage))
        button_results.grid(row=0,column=3)
        
    def add_postit(self,x,y,exp = 0, btn_id = None): 
        
        #TODO change the add button to a standalone in the last position

        if btn_id != 0 and btn_id != None: #destroys the 'add' button for the first postit
            self.add_buttons[btn_id-1].destroy() 

        if exp == 0:

            cursor.execute("INSERT INTO experiments DEFAULT VALUES")
            current_experiment = cursor.execute("SELECT * FROM experiments ORDER BY id DESC LIMIT 1").fetchone()[0]
            cnx.commit()
            side = tk.LEFT
            exp = 1
        else:               

            current_experiment = exp
            side = tk.RIGHT

        canvas = tk.Canvas(self, relief = tk.FLAT, background = "#FFFF00",
                                            width = 300, height = 200)
        canvas.grid(row=x,column=y)
        self.canvas_l.append(canvas)
        #defines the n+1 post it's position
        if y == 3:
            y = 0
            x += 1
        else:
            y += 1
            
        button_add = tk.Button(self, text = "Add", command = lambda: self.add_postit(x,y,btn_id=(current_experiment)), anchor = tk.W)
        self.add_buttons.append(button_add)                
        button_window = canvas.create_window(10, 150, anchor=tk.NW, window=button_add)
        
        label_exp = tk.Label(self,text="Experiment %i" % (current_experiment),anchor=tk.CENTER)
        label_window =  canvas.create_window(140,50,anchor=tk.CENTER,window=label_exp)

        button_edit = tk.Button(self, text = "Edit", command = lambda: self.create_edit_windows(exp), anchor = tk.W)
        buttone_window =  canvas.create_window(50, 150, anchor=tk.NW, window=button_edit)

        button_simulation = tk.Button(self, text = "Simulate", command = lambda: vissim_simulation(exp), anchor = tk.W)
        buttons_window =  canvas.create_window(110, 150, anchor=tk.NW, window=button_simulation)

        #button_results = tk.Button(self, text = "Results", command = lambda: self.create_result_window(exp), anchor = tk.W)
        #buttonself =  canvas.create_window(170, 150, anchor=tk.NW, window=button_results)

        button_delete = tk.Button(self, text = "Delete", command = lambda: self.delete_postit(exp=current_experiment), anchor = tk.W)
        buttond_window =  canvas.create_window(230, 150, anchor=tk.NW, window=button_delete)
        
    def create_edit_windows(self,exp):

        configurations = len(self.datapoints_df.loc[self.datapoints_df['experiment']==exp])
        if configurations == 0:
            configurations = 1

        win = tk.Toplevel()
        win.wm_title("Edit experiment")
        
        print('configurations')
        print(configurations)

        for i in range(configurations):

            edit_windows(experiment=exp,parent = win, cfg=(i+1),new=1)

        
        #print(self.experiment_data)

    def delete_postit(self,exp):
        print(self.canvas_l)
        cursor.execute('DELETE FROM datapoints WHERE experiment = ?', (int(exp),))
        cursor.execute('DELETE FROM simulation_cfg WHERE experiment = ?',(int(exp),))
        cursor.execute('DELETE FROM parameters WHERE experiment = ?',(int(exp),))
        cursor.execute('DELETE FROM experiments WHERE id = ?',(int(exp),))
        cursor.execute('REINDEX experiments') #FIXME nao funciona, a tabela experimetns vazia tem ids que quebram o codigo
        cnx.commit() 
        self.canvas_l[exp-1].destroy() 
class edit_windows(tk.Frame):

    def __init__(self,parent,experiment,cfg,new):

        print('cfg:%i' % cfg)

        tk.Frame.__init__(self)

        query_dp = str('SELECT * FROM datapoints WHERE experiment = #exp').replace('#exp',str(experiment))
        query_pa = str('SELECT * FROM parameters WHERE experiment = #exp').replace('#exp',str(experiment))
        query_sim = str('SELECT * FROM simulation_cfg WHERE experiment = #exp').replace('#exp',str(experiment))

        self.datapoints_df = pd.read_sql(query_dp, cnx)  
        self.parameters_df = pd.read_sql(query_pa, cnx)  
        self.simulations_cfg = pd.read_sql(query_sim, cnx)

        if len(self.datapoints_df.index) == len(self.parameters_df.index) == len(self.simulations_cfg.index) == 0 or new == 0:
 
            cursor.execute("INSERT INTO datapoints (experiment) VALUES (%s)" % (experiment))     
            cursor.execute("INSERT INTO parameters (experiment) VALUES (%s)" % (experiment))                                                                                             
            cursor.execute("INSERT INTO simulation_cfg (experiment) VALUES (%s)" % (experiment))            

            self.datapoints_df = pd.read_sql(query_dp, cnx)
            self.parameters_df = pd.read_sql(query_pa, cnx)
            self.simulations_cfg = pd.read_sql(query_sim, cnx)

            self.datapoints_ctype_svar = tk.StringVar()
            self.datapoints_ctype_svar.set('Select a datapoint for displaying in the results')
            self.datapoints_cperfmeasure_dropdown_svar = tk.StringVar()
            self.datapoints_cperfmeasure_dropdown_svar.set('Select a perfomance measure')
            self.datapoints_ctimeinterval_svar = tk.StringVar()
            self.datapoints_ctimeinterval_svar.set('Select a time interval')
            self.datapoints_ctargetvalue_svar = tk.StringVar()
            self.datapoints_ctargetvalue_svar.set('Enter a field value')
            self.parameter_search_listbox_svar = tk.StringVar()
            self.parameter_search_listbox_svar.set('Search parameters here')  
            self.parameter_entry_liminf_svar = tk.StringVar()
            self.parameter_entry_liminf_svar.set('Set the inferior limit for parameter value')
            self.parameter_entry_limsup_svar = tk.StringVar()
            self.parameter_entry_limsup_svar.set('Set the superior limit for parameter value')
            self.parameter_entry_step_svar = tk.StringVar()
            self.parameter_entry_step_svar.set('Set the increment on the parameter')
            self.simulation_entry_replications_svar = tk.StringVar()
            self.simulation_entry_replications_svar.set('How many replications?')
            self.simulation_entry_seed_svar = tk.StringVar()
            self.simulation_entry_seed_svar.set('Set a initial seed')
            self.simulation_entry_seed_i_svar = tk.StringVar()
            self.simulation_entry_seed_i_svar.set('Set an increment')
            self.datapoints_df = self.datapoints_df.iloc[cfg-1]
            self.parameters_df = self.parameters_df.iloc[cfg-1]
            self.simulations_cfg = self.simulations_cfg.iloc[cfg-1]

        else:

            self.datapoints_df = self.datapoints_df.iloc[cfg-1]
            self.parameters_df = self.parameters_df.iloc[cfg-1]
            self.simulations_cfg = self.simulations_cfg.iloc[cfg-1] 


            if self.datapoints_df.isnull().any() or self.parameters_df.isnull().any() or self.simulations_cfg.isnull().any():

                self.datapoints_ctype_svar = tk.StringVar()
                self.datapoints_ctype_svar.set('Select a datapoint for displaying in the results')
                self.datapoints_cperfmeasure_dropdown_svar = tk.StringVar()
                self.datapoints_cperfmeasure_dropdown_svar.set('Select a perfomance measure')
                self.datapoints_ctimeinterval_svar = tk.StringVar()
                self.datapoints_ctimeinterval_svar.set('Select a time interval')
                self.datapoints_ctargetvalue_svar = tk.StringVar()
                self.datapoints_ctargetvalue_svar.set('Enter a field value')
                self.parameter_search_listbox_svar = tk.StringVar()
                self.parameter_search_listbox_svar.set('Search parameters here')  
                self.parameter_entry_liminf_svar = tk.StringVar()
                self.parameter_entry_liminf_svar.set('Set the inferior limit for parameter value')
                self.parameter_entry_limsup_svar = tk.StringVar()
                self.parameter_entry_limsup_svar.set('Set the superior limit for parameter value')
                self.parameter_entry_step_svar = tk.StringVar()
                self.parameter_entry_step_svar.set('Set the increment on the parameter')
                self.simulation_entry_replications_svar = tk.StringVar()
                self.simulation_entry_replications_svar.set('How many replications?')
                self.simulation_entry_seed_svar = tk.StringVar()
                self.simulation_entry_seed_svar.set('Set a initial seed')
                self.simulation_entry_seed_i_svar = tk.StringVar()
                self.simulation_entry_seed_i_svar.set('Set an increment')
            
            else:
                self.datapoints_ctype_svar = tk.StringVar()
                self.datapoints_ctype_svar.set(self.datapoints_df['dc_type']+' / '+str(self.datapoints_df['dc_number']))
                self.datapoints_cperfmeasure_dropdown_svar = tk.StringVar()
                self.datapoints_cperfmeasure_dropdown_svar.set(self.datapoints_df['perf_measure'])
                self.datapoints_ctimeinterval_svar = tk.StringVar()
                self.datapoints_ctimeinterval_svar.set(self.datapoints_df['time_p'])
                self.datapoints_ctargetvalue_svar = tk.StringVar()
                self.datapoints_ctargetvalue_svar.set(self.datapoints_df['field_value'])
                self.parameter_search_listbox_svar = tk.StringVar()
                self.parameter_search_listbox_svar.set(self.parameters_df['parameter_name'])  
                self.parameter_entry_liminf_svar = tk.StringVar()
                self.parameter_entry_liminf_svar.set(self.parameters_df['parameter_b_value'])
                self.parameter_entry_limsup_svar = tk.StringVar()
                self.parameter_entry_limsup_svar.set(self.parameters_df['parameter_u_value'])
                self.parameter_entry_step_svar = tk.StringVar()
                self.parameter_entry_step_svar.set(self.parameters_df['parameter_step'])
                self.simulation_entry_replications_svar = tk.StringVar()
                self.simulation_entry_replications_svar.set(self.simulations_cfg['replications'])
                self.simulation_entry_seed_svar = tk.StringVar()
                self.simulation_entry_seed_svar.set(self.simulations_cfg['initial_seed'])
                self.simulation_entry_seed_i_svar = tk.StringVar()
                self.simulation_entry_seed_i_svar.set(self.simulations_cfg['seed_increment'])

        
        self.win = parent
        #self.win.protocol("WM_DELETE_WINDOW", self.on_closing)
        #configurations = len(self.datapoints_df.loc[self.datapoints_df['experiment']==experiment])

        self.subframe = tk.Frame(self.win,height = 400, width = 400,highlightbackground="red", highlightcolor="red",highlightthickness=1,bd =0)
        self.subframe.grid(row=1+cfg,column=1)

        #b = tk.Button(self.subframe, text="Okay", command=lambda:  win.destroy)

        self.search_var = tk.StringVar()
        self.switch = False
        self.search_mem = ''

        self.datapoints_label = tk.Label(self.subframe,text = 'Data Points')
        
        self.datapoints_ctype_dropdown = ttk.Combobox(self.subframe, width=25,textvariable=self.datapoints_ctype_svar,state='readonly')
        self.datapoints_ctype_dropdown['values'] = list(dc_data['Display'])
        self.datapoints_ctype_dropdown.configure(font=('Roboto', 8))
        #self.datapoints_ctype_dropdown.set(self.datapoints_ctype_svar)
        self.datapoints_ctype_dropdown.bind('<<ComboboxSelected>>', lambda e: self.datapoints_callback(eventObject=e,experiment = experiment))

        self.separatorv = ttk.Separator(self.subframe, orient="vertical")

        self.datapoints_cperfmeasure_dropdown = ttk.Combobox(self.subframe,textvariable=self.datapoints_cperfmeasure_dropdown_svar, width=25)
        self.datapoints_cperfmeasure_dropdown['values'] = []
        self.datapoints_cperfmeasure_dropdown.configure(font=('Roboto', 8))
        #self.datapoints_cperfmeasure_dropdown.set('Select what you will measure')        
        self.datapoints_cperfmeasure_dropdown.bind('<<ComboboxSelected>>', lambda e: self.datapoints_callback(eventObject=e,experiment = experiment))

        self.datapoints_ctimeinterval_label = tk.Label(self.subframe, text='Add time interval number or agregation \n eg: 1,2,3,avg,min,max')        
        self.datapoints_ctimeinterval_entry = tk.Entry(self.subframe,textvariable=self.datapoints_ctimeinterval_svar)

        self.datapoints_ctargetvalue_label=tk.Label(self.subframe, text='Add the field data to compare')
        self.datapoints_ctargetvalue_entry= tk.Entry(self.subframe, textvariable = self.datapoints_ctargetvalue_svar)
        self.datapoint_ok_button = tk.Button(self.subframe, text="Save Changes", command = lambda: self.save_exp_cfg(experiment,db_ids=[self.datapoints_df['ID'],self.simulations_cfg['ID'],self.parameters_df['ID']]))# image=self.check_image)
        
        ##------Parameters section------##
        self.parameters_label = tk.Label(self.subframe,text = 'Parameters')


        self.parameter_search_entry = tk.Entry(self.subframe, textvariable=self.search_var, width=25)    
        self.parameter_search_entry.insert(0, self.parameter_search_listbox_svar.get())       

        self.parameter_search_listbox = tk.Listbox(self.subframe, width=45, height=1)
        self.parameter_search_listbox.bind('<<ListboxSelect>>',  lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        self.parameter_label_liminf = tk.Label(self.subframe, text = 'Inferior Limit')
        self.parameter_entry_liminf = tk.Entry(self.subframe, width=10, textvariable = self.parameter_entry_liminf_svar)
        self.parameter_entry_liminf.bind('<FocusOut>', lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        self.parameter_label_limsup = tk.Label(self.subframe, text = 'Superior Limit')
        self.parameter_entry_limsup = tk.Entry(self.subframe, width=10,textvariable = self.parameter_entry_limsup_svar)
        self.parameter_entry_limsup.bind('<FocusOut>',lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        self.parameter_label_step = tk.Label(self.subframe, text = 'Step')

        self.parameter_entry_step = tk.Entry(self.subframe, width=10, textvariable = self.parameter_entry_step_svar)
        self.parameter_entry_step.bind('<Leave>',lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        ##------Simulation section------##
        self.simulation_label = tk.Label(self.subframe, text = 'Simulation Configs')

        self.simulation_label_replications = tk.Label(self.subframe, text = 'How many runs?')
        self.simulation_entry_replications = tk.Entry(self.subframe, width=5, textvariable = self.simulation_entry_replications_svar)

        self.simulation_label_seed = tk.Label(self.subframe, text = 'Set initial seed')
        self.simulation_entry_seed = tk.Entry(self.subframe, width=5, textvariable = self.simulation_entry_seed_svar)

        self.simulation_label_seed_i = tk.Label(self.subframe, text = 'Set increment')
        self.simulation_entry_seed_i = tk.Entry(self.subframe, width=5, textvariable = self.simulation_entry_seed_i_svar)

        ##------New button--------------##
        self.new_button = tk.Button(self.subframe, text = '+', command = lambda: edit_windows(experiment=experiment,parent = self.win, cfg=(cfg+1),new=0))
        self.new_button.grid(row=9, column=5, sticky='w',padx=10)
        ##------Delete button--------------##
        self.del_button = tk.Button(self.subframe, text = 'X', command = lambda: self.destroy_exp_cfg(db_ids=[self.datapoints_df['ID'],self.simulations_cfg['ID'],self.parameters_df['ID']]))
        self.del_button.grid(row=9, column=6, sticky='w',padx=10)
        ##------Grid configuration------##
    
        self.datapoints_label.grid(row=2, column=0, sticky='w', padx=10)
        self.datapoints_ctype_dropdown.grid(row=4, column=0, sticky='w', padx=10)
        self.datapoints_cperfmeasure_dropdown.grid(row=4, column=1, sticky='w', padx=10)
        self.datapoints_ctimeinterval_label.grid(row=3, column=2, sticky='w', padx=10)
        self.datapoints_ctimeinterval_entry.grid(row=4, column=2, sticky='w', padx=10)
        self.datapoints_ctargetvalue_label.grid(row=3, column=3, sticky='w', padx=10)
        self.datapoints_ctargetvalue_entry.grid(row=4, column=3, sticky='w', padx=10)
        self.datapoint_ok_button.grid(row=4, column=4, sticky='w', padx=10)
        self.separatorv.grid(row=8, column=5, sticky='ns', rowspan=100)
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
        self.simulation_label_seed.grid(row=7, column=0, sticky='w', padx=10)
        self.simulation_entry_seed.grid(row=7, column=1, sticky='w', padx=10)
        self.simulation_label_seed_i.grid(row=8, column=0, sticky='w', padx=10)
        self.simulation_entry_seed_i.grid(row=8, column=1, sticky='w', padx=10)
        
        #Function for updating the list/doing the search.
        #It needs to be called here to populate the listbox
        self.update_list()
        self.poll()

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
                
        lbox_list = list(parameter_db['Long Name'])
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

    def save_exp_cfg(self,experiment,db_ids): #save button


        self.datapoints_df.loc['field_value'] = self.datapoints_ctargetvalue_entry.get()
        self.datapoints_df.loc['time_p'] = self.datapoints_ctimeinterval_entry.get()

        self.simulations_cfg.loc['replications'] = self.simulation_entry_replications.get()
        self.simulations_cfg.loc['initial_seed'] = self.simulation_entry_seed.get()
        self.simulations_cfg.loc['seed_increment'] = self.simulation_entry_seed_i.get()

        self.datapoints_df = self.datapoints_df.to_frame().T
        self.simulations_cfg = self.simulations_cfg.to_frame().T
        self.parameters_df = self.parameters_df.to_frame().T

        print('----------')
        print(self.datapoints_df)
        print(self.simulations_cfg)
        print(self.parameters_df)
        print('----------')

        cursor.execute("""UPDATE datapoints 
                            SET dc_type = ?, dc_number = ?, perf_measure = ?,field_value = ?, time_p = ? 
                            WHERE ID = ?""" ,(str(self.datapoints_df['dc_type'].item()),int(self.datapoints_df['dc_number'].item()),
                                                str(self.datapoints_df['perf_measure'].item()),float(self.datapoints_df['field_value'].item()),
                                                str(self.datapoints_df['time_p'].item()),db_ids[0]))
        cursor.execute("""UPDATE simulation_cfg 
                            SET replications = ?, initial_seed = ?, seed_increment = ? 
                            WHERE ID =?""", (self.simulations_cfg['replications'].item(),self.simulations_cfg['initial_seed'].item(),
                                                self.simulations_cfg['seed_increment'].item(),db_ids[1]))
        cursor.execute("""UPDATE parameters 
                            SET parameter_name = ?, parameter_b_value = ?, parameter_u_value = ?, parameter_step = ? 
                            WHERE ID = ?""", (self.parameters_df['parameter_name'].item(),self.parameters_df['parameter_b_value'].item(),
                                                self.parameters_df['parameter_u_value'].item(),self.parameters_df['parameter_step'].item(),db_ids[2]))
        cnx.commit() #TODO Fazer com que todo o programa trabalhe com tabelas temporárias enquanto o user nao der "save"

    def destroy_exp_cfg(self, db_ids):
        print(db_ids)

        cursor.execute('DELETE FROM datapoints WHERE ID = ?', (int(db_ids[0]),))
        cursor.execute('DELETE FROM simulation_cfg WHERE ID = ?',(int(db_ids[1]),))
        cursor.execute('DELETE FROM parameters WHERE ID = ?',(int(db_ids[2]),))
        cnx.commit()
        self.subframe.destroy()

    def parameters_callback(self,experiment, eventObject):
        
        caller = str(eventObject.widget)

        if 'listbox' in caller:
            #print(self.parameter_search_listbox)
            selected = self.parameter_search_listbox.curselection()
            parameter_text = self.parameter_search_listbox.get(first=selected, last=None)

            parameter_identifier_row = parameter_db.loc[parameter_db['Long Name']==parameter_text]
            
            value = str(parameter_identifier_row['Identifier'].item())
            
            self.parameters_df.loc['parameter_name'] = value

            print(self.parameters_df)

        else:

            value = eventObject.widget.get()
            print(value)        

        if 'entry4' in caller: #liminf          
           self.parameters_df.loc['parameter_b_value'] = value
           print(self.parameters_df)
    
        elif 'entry5' in caller: #limsup  
           self.parameters_df.loc['parameter_u_value'] = value
           print(self.parameters_df)

        elif 'entry6' in caller: #step
           self.parameters_df.loc['parameter_step'] = value
           print(self.parameters_df)
        
        '''else:
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            dc_match = dc_data.loc[dc_data['Display'] == value]
            data_point_type = dc_match['Type'].item()
            Dc_Number = dc_match['No'].item()

            self.experiment_data.loc[experiment_index, 'Data Point Type'] = data_point_type
            self.experiment_data.loc[experiment_index, 'DP Number'] = Dc_Number
            print(self.experiment_data)'''
        
        #print(self.experiment_data)
        
    def datapoints_callback(self, eventObject, experiment): 
        # you can also get the value off the eventObject
        caller = str(eventObject.widget)
        value = eventObject.widget.get()
        #print(caller)
        #print(value)
        print(self.datapoints_df)

        if caller == None:
            entry_value = self.datapoints_ctargetvalue_entry.get()
            #print(entry_value)
            #experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            self.datapoints_df.loc['field_value'] = entry_value
            print(self.datapoints_df)
    
        elif 'combobox2' in caller:  
            print('selected1')       
            #experiment_index  = self.experiment_df.loc[self.experiment_df['Experiment']==self.experiment].index[0]
            self.datapoints_df.loc['perf_measure'] = value
            print(self.datapoints_df)

        elif 'combobox3' in caller:
            #experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            self.datapoints_df.loc['time_p'] = value
            print(self.datapoints_df)

        else:
            print(self.datapoints_df)
            #experiment_index  = self.experiment_df.loc[self.experiment_df['Experiment']==self.experiment].index[0]
            dc_match = dc_data.loc[dc_data['Display'] == value]
            data_point_type = dc_match['Type'].item()
            Dc_Number = dc_match['No'].item()         
            
            self.datapoints_df.loc['dc_type'] = data_point_type
            self.datapoints_df.loc['dc_number'] = Dc_Number

            if data_point_type == 'Data Collector':
                self.datapoints_cperfmeasure_dropdown['values'] = ['QueueDelay', 'SpeedAvgArith', 'OccupRate','Acceleration', 'Lenght', 'Vehs', 'Pers','Saturation Headway']

            elif data_point_type == 'Travel Time Collector':
                self.datapoints_cperfmeasure_dropdown['values'] = ['StopDelay', 'Stops', 'VehDelay', 'Vehs', 'Persons Delay', 'Persons']
                
            else:
                self.datapoints_cperfmeasure_dropdown['values'] = ['QLen', 'QLenMax', 'QStops']

            print(self.datapoints_df)    
class ResultsPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self,parent)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff",height='800',width='1510')
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((6,6), window=self.frame, anchor="nw", 
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        label = tk.Label(self.frame, text="Results Dashboard", font=LARGE_FONT)
        label.grid(row=0,column=0)
 
        button = tk.Button(self.frame, text="Experiment board",
                            command=lambda: controller.show_frame(Board))
        button.grid(row=0,column=1)

        button2 = tk.Button(self.frame, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button2.grid(row=0,column=2)

        #loading data
        existing_experiments_qry = "SELECT * FROM experiments"
        existing_experiments = pd.read_sql(existing_experiments_qry,cnx)

        self.datapoints_df = pd.read_sql(str('SELECT * FROM datapoints'), cnx)
        self.parameters_df = pd.read_sql(str('SELECT * FROM parameters'), cnx)
        self.simulation_runs = pd.read_sql(str('SELECT * FROM simulation_runs'), cnx)

        #Line chart
        lineChart_frame = tk.Frame(self.frame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        lineChart_frame.grid(row=1,column=0,sticky='w')
        lineChart_label = tk.Label(lineChart_frame,text="" ,anchor=tk.E)
        lineChart_label.grid(row=0, column=1)
        
        self.lineChart_svar = tk.StringVar()
        self.lineChart_svar.set('Select a experiment')
        lineChart_cbbox = ttk.Combobox(lineChart_frame, width=5,textvariable=str(self.lineChart_svar),state='readonly')
        lineChart_cbbox['values'] = list(existing_experiments['id'])
        lineChart_cbbox.bind('<<ComboboxSelected>>', lambda e: self.plotLinechart(eventObject = e)) 
        lineChart_cbbox.grid(row=3,column=1)

        self.lineChart_plot = Figure(figsize=(5,4), dpi=100)
        self.lineChart_subplot = self.lineChart_plot.add_subplot(111)

        self.lineChart_canvas = FigureCanvasTkAgg(self.lineChart_plot, lineChart_frame) 
        self.lineChart_canvas.draw()
        self.lineChart_canvas._tkcanvas.grid(row=3,column=0,sticky='e')
        lineChart_tframe = tk.Frame(lineChart_frame)
        lineChart_tframe.grid(row=4,column=0)
        lineChart_toolbar = NavigationToolbar2Tk(self.lineChart_canvas,lineChart_tframe)

        #Scatter chart
        
        scatterChart_frame = tk.Frame(self.frame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        scatterChart_frame.grid(row=2,column=0)
        scatterChart_label = tk.Label(scatterChart_frame,text="" ,anchor=tk.E)
        scatterChart_label.grid(row=0, column=1)        
        scatterChart_framewidget = tk.Frame(scatterChart_frame)
        scatterChart_framewidget.grid(row=3,column=1, sticky='w')

        self.scatterChart_esvar = tk.StringVar()
        self.scatterChart_esvar.set('Select a experiment')
        scatterChart_ecbbox = ttk.Combobox(scatterChart_framewidget, width=5,textvariable=str(self.scatterChart_esvar),state='readonly')
        scatterChart_ecbbox['values'] = list(existing_experiments['id'])
        scatterChart_ecbbox.bind('<<ComboboxSelected>>', lambda e: self.expSelect(eventObject = e)) 
        scatterChart_ecbbox.grid(row=0,column=0, sticky='w')

        self.scatterChart_p1svar = tk.StringVar()
        self.scatterChart_p1svar.set('Select a parameter level')
        self.scatterChart_p1cbbox = ttk.Combobox(scatterChart_framewidget, width=30,textvariable=str(self.scatterChart_p1svar),state='readonly')
        self.scatterChart_p1cbbox['values'] = []
        self.scatterChart_p1cbbox.bind('<<ComboboxSelected>>', lambda e: self.plotScatterchart(eventObject = e)) 
        self.scatterChart_p1cbbox.grid(row=1,column=0, sticky='w')

        self.scatterChart_p2svar = tk.StringVar()
        self.scatterChart_p2svar.set('Select another parameter level')
        self.scatterChart_p2cbbox = ttk.Combobox(scatterChart_framewidget, width=30,textvariable=str(self.scatterChart_p2svar),state='readonly')
        self.scatterChart_p2cbbox['values'] = []
        self.scatterChart_p2cbbox.bind('<<ComboboxSelected>>', lambda e: self.plotScatterchart(eventObject = e)) 
        self.scatterChart_p2cbbox.grid(row=2,column=0, sticky='w')

        self.scatterChart_plot = Figure(figsize=(5,4), dpi=100)
        self.scatterChart_subplot = self.scatterChart_plot.add_subplot(111)

        self.scatterChart_canvas = FigureCanvasTkAgg(self.scatterChart_plot, scatterChart_frame) 
        self.scatterChart_canvas.draw()
        self.scatterChart_canvas._tkcanvas.grid(row=3,column=0)
        scatterChart_tframe = tk.Frame(scatterChart_frame)
        scatterChart_tframe.grid(row=4,column=0)
        scatterChart_toolbar = NavigationToolbar2Tk(self.scatterChart_canvas,scatterChart_tframe)

        #Boxplot 

        self.boxplotFrame = tk.Frame(self.frame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        self.boxplotFrame.grid(row=1,column=1)

        self.boxplotWidgetframe = tk.Frame(self.boxplotFrame)
        self.boxplotWidgetframe.grid(row=0,column=1)

        self.boxplotSvar = tk.StringVar()
        self.boxplotSvar.set('Select an experiment')
        self.boxplotexpCbbox = ttk.Combobox(self.boxplotWidgetframe,width=15,textvariable=str(self.boxplotSvar),state='readonly')
        self.boxplotexpCbbox['values'] = list(existing_experiments['id'])
        self.boxplotexpCbbox.bind('<<ComboboxSelected>>', lambda e: self.boxPlot(eventObject=e))
        self.boxplotexpCbbox.grid(row=1,column=1)

        self.boxplotFigure = Figure(figsize=(5,4), dpi=100)
        self.boxplotSubplot = self.boxplotFigure.add_subplot(111)
        self.boxplotCanvas = FigureCanvasTkAgg(self.boxplotFigure, self.boxplotFrame)
        self.boxplotCanvas.draw()
        self.boxplotCanvas._tkcanvas.grid(row=0,column=0)
        self.boxplotTFrame = tk.Frame(self.boxplotFrame)
        self.boxplotTFrame.grid(row=1,column=0)
        self.boxplotToolbar = NavigationToolbar2Tk(self.boxplotCanvas, self.boxplotTFrame)
        
        #Boxplot c/ I.C

        self.ciboxplotFrame = tk.Frame(self.frame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        self.ciboxplotFrame.grid(row=2,column=1)
        self.ciboxplotWidgetframe = tk.Frame(self.ciboxplotFrame)
        self.ciboxplotWidgetframe.grid(row=0,column=1)
        self.ciboxplotSvar = tk.StringVar()
        self.ciboxplotSvar.set('Select an experiment')
        self.ciboxplotexpCbbox = ttk.Combobox(self.ciboxplotWidgetframe,width=15,textvariable=str(self.ciboxplotSvar),state='readonly')
        self.ciboxplotexpCbbox['values'] = list(existing_experiments['id'])
        self.ciboxplotexpCbbox.bind('<<ComboboxSelected>>', lambda e: self.ciboxPlot(eventObject=e))
        self.ciboxplotexpCbbox.grid(row=1,column=1)
        self.ciboxplotFigure = Figure(figsize=(5,4), dpi=100)
        self.ciboxplotSubplot = self.ciboxplotFigure.add_subplot(111)
        self.ciboxplotCanvas = FigureCanvasTkAgg(self.ciboxplotFigure, self.ciboxplotFrame)
        self.ciboxplotCanvas.draw()
        self.ciboxplotCanvas._tkcanvas.grid(row=0,column=0)
        self.ciboxplotTFrame = tk.Frame(self.ciboxplotFrame)
        self.ciboxplotTFrame.grid(row=1,column=0)
        self.ciboxplotToolbar = NavigationToolbar2Tk(self.ciboxplotCanvas, self.ciboxplotTFrame)


        #Dif. means
        #Here how to use StatsModels' CompareMeans to calculate the confidence interval for the difference between means:
        self.difmeansFrame = tk.Frame(self.frame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        self.difmeansFrame.grid(row=3,column=1)
        self.difmeansMainText = tk.Label(self.difmeansFrame, text="Difference of means test", anchor=tk.CENTER)
        self.difmeansMainText.grid(row=0,column=0)

        self.difmeansSvar1 = tk.StringVar()
        self.difmeansSvar1.set('Select an experiment')
        self.difmeansExp1Cbbox = ttk.Combobox(self.difmeansFrame,width=15,textvariable=str(self.difmeansSvar1),state='readonly')
        self.difmeansExp1Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansExp1Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelect(eventObject=e))
        self.difmeansExp1Cbbox.grid(row=1,column=0)

        self.difmeansSvarp1 = tk.StringVar()
        self.difmeansSvarp1.set('Select a param. profile')
        self.difmeansCbboxp1 = ttk.Combobox(self.difmeansFrame,width=30,textvariable=str(self.difmeansSvarp1),state='readonly')
        self.difmeansCbboxp1['values'] = []
        #self.difmeansCbboxp1.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelect(eventObject=e))
        self.difmeansCbboxp1.grid(row=1,column=1)

        self.difmeansSvar2 = tk.StringVar()
        self.difmeansSvar2.set('Select an experiment')
        self.difmeansExp2Cbbox = ttk.Combobox(self.difmeansFrame,width=15,textvariable=str(self.difmeansSvar2),state='readonly')
        self.difmeansExp2Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansExp2Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelect(eventObject=e))
        self.difmeansExp2Cbbox.grid(row=2,column=0)

        self.difmeansSvarp2 = tk.StringVar()
        self.difmeansSvarp2.set('Select a param. profile')
        self.difmeansCbboxp2 = ttk.Combobox(self.difmeansFrame,width=30,textvariable=str(self.difmeansSvarp2),state='readonly')
        self.difmeansCbboxp2['values'] = []
        #self.difmeansCbboxp2.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelect(eventObject=e,tp=1))
        self.difmeansCbboxp2.grid(row=2,column=1)

        self.genButton = ttk.Button(self.difmeansFrame,text='Generate report', command= self.difmeanReport)
        self.genButton.grid(row=3,column=0)
    def difmeanReport(self):

        try:            

            #Data loading
            exp1 = self.difmeansExp1Cbbox.get()
            exp2 = self.difmeansExp2Cbbox.get()
            par1 = self.cfgsDict[self.difmeansCbboxp1.get()]
            print(par1)
            par2 = self.cfgsDict[self.difmeansCbboxp2.get()]
            print(par2)
            dados_1 = pd.read_sql('select * from simulation_runs where experiment = %s and sim_perf = %s' % (exp1,par1),cnx)['results'].drop_duplicates()
            dados_2 = pd.read_sql('select * from simulation_runs where experiment = %s and sim_perf = %s' % (exp2,par2),cnx)['results'].drop_duplicates()
            #frontend
            print('clicked')
            reportWin = tk.Toplevel()
            reportWin.wm_title("Edit experiment")
            frame = tk.Frame(reportWin)
            frame.grid(row=0,column=0)

            #Analysis
            linreg = stats.linregress(dados_1, dados_2)
            
            mean1 = dados_1.mean()
            mean2 = dados_2.mean()
            n = dados_2.count()
            var1 = dados_1.std()**2
            var2 = dados_2.std()**2
            r_values = stats.pearsonr(dados_1,dados_2)
            r = r_values[0]
            r_p = r_values[1]
            df = n-1
            statt = stats.ttest_rel(dados_1,dados_2)

            if r_p < 0.05:
                #dependent
                d_test = stats.ttest_rel(dados_1,dados_2)
                tp = 'Paired'
            else:
                i_test = stats.ttest_ind(dados_1,dados_2,equal_var=False)
                tp = 'Independent'
            teste = {'mean1':[mean1],'mean2':[mean2],'var1':[var1],'var2':[var2],'n':[n],'r':[r],'h0':[0],'df':[df],'statt':[i_test[0]],'pvalue':[i_test[1]],'type':tp}    
            teste_df = pd.DataFrame.from_dict(teste) 

            testLabel = tk.Label(frame,text='T test: paired sample mean difference')
            testLabel.grid(row=0,column=2)

            var1Label = tk.Label(frame,text='Variable 1')
            var1Label.grid(row=1,column=2)

            var2Label = tk.Label(frame,text='Variable 2')
            var2Label.grid(row=1,column=4)

            meanLabel = tk.Label(frame,text='Mean')
            meanLabel.grid(row=2,column=0)
            mean1Value = tk.Label(frame,text=teste['mean1'])
            mean1Value.grid(row=2,column=2)
            mean2Value = tk.Label(frame,text=teste['mean2'])
            mean2Value.grid(row=2,column=4)

            varLabel = tk.Label(frame,text='Variance')
            varLabel.grid(row=3,column=0)
            var1Value = tk.Label(frame,text=teste['var1'])
            var1Value.grid(row=3,column=2)
            var2Value = tk.Label(frame,text=teste['var2'])
            var2Value.grid(row=3,column=4)

            obsLabel = tk.Label(frame,text='Observation')
            obsLabel.grid(row=4,column=0)
            obsValue = tk.Label(frame,text=teste['n'])
            obsValue.grid(row=4,column=2)

            pearsonLabel = tk.Label(frame,text='Pearson Correlation')
            pearsonLabel.grid(row=5,column=0)
            pearsonValue = tk.Label(frame,text=teste['r'])
            pearsonValue.grid(row=5,column=2)

            pearsonLabel = tk.Label(frame,text='Type test')
            pearsonLabel.grid(row=6,column=0)
            pearsonValue = tk.Label(frame,text=teste['type'])
            pearsonValue.grid(row=6,column=2)

            h0Label = tk.Label(frame,text='Mean difference hypothesis')
            h0Label.grid(row=7,column=0)
            h0Value = tk.Label(frame,text=teste['h0'])
            h0Value.grid(row=7,column=2)

            dfLabel = tk.Label(frame,text='Degrees of freedom')
            dfLabel.grid(row=8,column=0)
            dfValue = tk.Label(frame,text=teste['df'])
            dfValue.grid(row=8,column=2)

            stattLabel = ttk.Label(frame,text='Stat t')
            stattLabel.grid(row=9,column=0)
            stattValue = ttk.Label(frame,text=teste['statt'])
            stattValue.grid(row=9,column=2)

            criticaltLabel = ttk.Label(frame,text='Two-tailed teste p-value')
            criticaltLabel.grid(row=10,column=0)
            criticaltValue = ttk.Label(frame,text=teste['pvalue'])
            criticaltValue.grid(row=10,column=2)

            vertical1 = ttk.Separator(frame, orient="vertical")
            vertical1.grid(row=0, column=1, sticky='ns', rowspan=100)
            vertical2 = ttk.Separator(frame, orient="vertical")
            vertical2.grid(row=0, column=3, sticky='ns', rowspan=100)

            blank = tk.Label(frame,text='')
            blank.grid(row=11,column=2)
            copyButton = ttk.Button(frame,text='Copy to clipboard',command= lambda: teste_df.to_clipboard())
            copyButton.grid(row=12,column=2)
        
        except:

            popup = tk.Tk()
            popup.wm_title("!")
            label = ttk.Label(popup, text='Please select parameters', font=NORM_FONT)
            label.pack(side="top", fill="x", pady=10)
            B1 = ttk.Button(popup, text="Okay boss", command = popup.destroy)
            B1.pack()
            popup.mainloop()

    def difmeanSelect(self,eventObject):


        exp = int(eventObject.widget.get())
        simData = self.simulation_runs.loc[self.simulation_runs['experiment'] == exp]
        simCfgs = list(simData['sim_perf'].drop_duplicates())
        labelTxt_ls = []
        self.cfgsDict = {}

        for cfg in simCfgs:

            txtData = simData.loc[simData['sim_perf']==cfg].drop_duplicates(subset='parameter_name')
            labelTxt = ''

            for index, row in txtData.iterrows():

                labelTxt = labelTxt + '|%s = %s|' % (str(row['parameter_name']),str(row['parameter_value']))

            self.cfgsDict[labelTxt] = cfg
            labelTxt_ls.append(labelTxt)

        if '3' in str(eventObject.widget):

            self.difmeansCbboxp2['values'] = labelTxt_ls
        
        else:

            self.difmeansCbboxp1['values'] = labelTxt_ls

    def expSelect(self,eventObject):

        exp = int(eventObject.widget.get())

        simData = self.simulation_runs.loc[self.simulation_runs['experiment'] == exp]
        simCfgs = list(simData['sim_perf'].drop_duplicates())
        labelTxt_ls = []
        self.cfgsDict = {}

        for cfg in simCfgs:

            y_data = list(simData.loc[simData['sim_perf']==cfg]['results'].drop_duplicates())
            x_data = list(simData.loc[simData['sim_perf']==cfg]['seed'].drop_duplicates())
            txtData = simData.loc[simData['sim_perf']==cfg].drop_duplicates(subset='parameter_name')
            labelTxt = ''

            for index, row in txtData.iterrows():

                labelTxt = labelTxt + '|%s = %s|' % (str(row['parameter_name']),str(row['parameter_value']))
                #print(labelTxt)

            self.cfgsDict[labelTxt] = cfg
            labelTxt_ls.append(labelTxt)
            #print(self.cfgsDict)
            #print(labelTxt_ls)

        self.scatterChart_p1cbbox['values'] = self.scatterChart_p2cbbox['values'] = labelTxt_ls   

    def plotLinechart(self,eventObject): #function that plots the line chart getting input from lineChart_cbbox
        
        self.lineChart_subplot.cla()

        exp = int(eventObject.widget.get())        
        simData = self.simulation_runs.loc[self.simulation_runs['experiment'] == exp]
        simCfgs = list(simData['sim_perf'].drop_duplicates())
        self.lineChart_subplot.set_title("Perf. Measure by Parameter and replication ")
        self.lineChart_subplot.set_ylabel(list(self.datapoints_df.loc[self.datapoints_df['experiment']==exp]['perf_measure'].drop_duplicates()))
        self.lineChart_subplot.set_xlabel('Simulation Run')

        for cfg in simCfgs:

            y_data = list(simData.loc[simData['sim_perf']==cfg]['results'].drop_duplicates())
            x_data = list(simData.loc[simData['sim_perf']==cfg]['seed'].drop_duplicates())
            txtData = simData.loc[simData['sim_perf']==cfg].drop_duplicates(subset='parameter_name')
            print(txtData)
            labelTxt = ''

            for index, row in txtData.iterrows():

                labelTxt = labelTxt + '|%s = %s|\n ' % (str(row['parameter_name']),str(row['parameter_value']))

            print(labelTxt)
            self.lineChart_subplot.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.,prop={'size': 8})
            self.lineChart_canvas.draw()
            self.lineChart_subplot.plot(x_data,y_data,label=labelTxt)
            self.lineChart_plot.subplots_adjust(right=0.64) #adjust legend problem here!

    def plotScatterchart(self,eventObject): #function that plots the scatter chart

        self.scatterChart_subplot.cla()

        exp = int(self.scatterChart_esvar.get())
        parPerf_key_1 = self.scatterChart_p1cbbox.get()
        parPerf_key_2 = self.scatterChart_p2cbbox.get()
        cfg_1 = self.cfgsDict[parPerf_key_1]
        cfg_2 = self.cfgsDict[parPerf_key_2]
        simData = self.simulation_runs.loc[self.simulation_runs['experiment'] == exp]
        simCfgs = list(simData['sim_perf'].drop_duplicates())
        labelTxt = str(parPerf_key_1) + str(' ') + str(parPerf_key_2)
        x_data = list(simData.loc[simData['sim_perf']==cfg_1]['results'].drop_duplicates())
        y_data = list(simData.loc[simData['sim_perf']==cfg_2]['results'].drop_duplicates())
        linreg = stats.linregress(x_data, y_data)
        r_squared = linreg.rvalue
        print(r_squared)
        #self.scatterChart_subplot.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.,prop={'size': 8})
        #self.scatterChart_subplot.text(x_data[0], y_data[0], 'R-squared = %0.2f' % r_squared)
        anchored_text = matplotlib.offsetbox.AnchoredText('R-squared = %0.2f \n P-value = %0.2f' % (r_squared,linreg.pvalue), loc=4, prop = dict(fontsize=8))
        
        self.scatterChart_subplot.add_artist(anchored_text)
        self.scatterChart_subplot.plot(np.unique(x_data), np.poly1d(np.polyfit(x_data, y_data, 1))(np.unique(x_data)))
        self.scatterChart_subplot.scatter(x_data,y_data)
        #self.scatterChart_plot.subplots_adjust(left=0.1) #adjust legend problem here!
        self.scatterChart_subplot.set_title(labelTxt,fontsize=8)
        self.scatterChart_subplot.set_ylabel(list(self.datapoints_df.loc[self.datapoints_df['experiment']==exp]['perf_measure'].drop_duplicates()))
        self.scatterChart_subplot.set_xlabel(list(self.datapoints_df.loc[self.datapoints_df['experiment']==exp]['perf_measure'].drop_duplicates()))
        self.scatterChart_canvas.draw()
        #self.scatterChart_subplot.tight_layout()

    def boxPlot(self, eventObject):

        self.boxplotSubplot.cla()

        exp = int(eventObject.widget.get())        
        simData = self.simulation_runs.loc[self.simulation_runs['experiment'] == exp]
        simCfgs = list(simData['sim_perf'].drop_duplicates())

        labels = []
        samples =[]

        for cfg in simCfgs:

            labelTxt=''

            samples.append(list(simData.loc[simData['sim_perf'] == cfg].drop_duplicates(subset='results')['results']))
            txtData = simData.loc[simData['sim_perf']==cfg].drop_duplicates(subset='parameter_name')
            #print(txtData)
            for index, row in txtData.iterrows():

                labelTxt = labelTxt + '%s = %s\n' % (str(row['parameter_name']),str(row['parameter_value']))
            labels.append(labelTxt)

        #print(labels)
        self.boxplotSubplot.set_xticklabels(labels,rotation=45,fontsize=8)     
        self.boxplotSubplot.set_ylabel(list(self.datapoints_df.loc[self.datapoints_df['experiment']==exp]['perf_measure'].drop_duplicates()))   
        self.boxplotSubplot.boxplot(samples)
        self.boxplotFigure.tight_layout()#subplots_adjust(bottom=0.15)
        self.boxplotCanvas.draw()

    def ciboxPlot(self,eventObject):
        
        self.boxplotSubplot.cla()

        exp = int(eventObject.widget.get())        
        simData = self.simulation_runs.loc[self.simulation_runs['experiment'] == exp]
        simCfgs = list(simData['sim_perf'].drop_duplicates())

        labels = []
        samples =[]

        for cfg in simCfgs:

            labelTxt=''

            samples.append(list(simData.loc[simData['sim_perf'] == cfg].drop_duplicates(subset='results')['results']))
            txtData = simData.loc[simData['sim_perf']==cfg].drop_duplicates(subset='parameter_name')
            #print(txtData)
            for index, row in txtData.iterrows():

                labelTxt = labelTxt + '%s = %s\n' % (str(row['parameter_name']),str(row['parameter_value']))
            labels.append(labelTxt)

        means = simData.groupby('sim_perf')['results'].mean().rename('mean')
        std = simData.groupby('sim_perf')['results'].std().rename('std')
        ns = simData.groupby('sim_perf')['results'].count().rename('count')
        simStats = pd.concat([means,std,ns],axis=1,sort=False)
        cis = []

        for index, stat in simStats.iterrows():
            
            ci = stats.t.interval(0.95, loc=stat['mean'], scale=stat['std']/np.sqrt(stat['count']),df=stat['count']-1)
            print(ci)
            cis.append(ci[1]-stat['mean'])

        print(cis)
        simStats.insert(1,'ci',value=cis)  

        x = list(labels)
        y = list(simStats['mean'])
        e = list(simStats['ci'])
        self.ciboxplotSubplot.set_xticklabels(labels,rotation=45,fontsize=8)
        self.ciboxplotSubplot.set_ylabel(list(self.datapoints_df.loc[self.datapoints_df['experiment']==exp]['perf_measure'].drop_duplicates()))   
        self.ciboxplotSubplot.errorbar(x, y, yerr=e, fmt='s',capsize=5)
        self.ciboxplotFigure.tight_layout()
        self.ciboxplotCanvas.draw()

    def onFrameConfigure(self, event):

        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class CalibrationPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self,parent)
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.place(in_=self, anchor="c", relx=.5, rely=.5)

        self.runPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\power.png")  #https://www.flaticon.com/packs/science-121
        self.cfgPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\settings.png")
        self.resultsPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\results.png")
        
        label = tk.Label(frame, text="Calibration", font=LARGE_FONT)
        label.grid(row=0,column=1)

        runLabel = tk.Label(frame, text="Run calibration")
        runLabel.grid(row=1,column=2)
        runButton = tk.Button(frame, text="Run calibration",
                            command=lambda: runCalibration,image=self.runPhoto)
        runButton.grid(row=2,column=2)

        cfgLabel = tk.Label(frame, text="Config calibration")
        cfgLabel.grid(row=1,column=1)
        cfgButton = tk.Button(frame, text="Config calibration",
                            command=lambda: cfgCalibration,image=self.cfgPhoto)
        cfgButton.grid(row=2,column=1)

        resultsLabel = tk.Label(frame, text="Results calibration")
        resultsLabel.grid(row=1,column=3)        
        resultsButton = tk.Button(frame, text="Results calibration",
                            command=lambda: resultsCalibration,image=self.resultsPhoto)
        resultsButton.grid(row=2,column=3)

class Calibration:

    #data initialization
    def __init__(self):

        cfgData = pd.read_sql()









app = SeaofBTCapp()
app.geometry("1920x1080")
app.state('zoomed')
app.mainloop()