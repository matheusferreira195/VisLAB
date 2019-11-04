# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:05:28 2019

@author: mathe
"""
import tkinter as tk
import sqlite3
import pandas as pd
import math
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

NORM_FONT= ("Roboto", 10)
LARGE_FONT = ("Roboto", 20)

#Database connection and set up

cnx = sqlite3.connect(r'E:\Google Drive\Scripts\VisLab\resources\vislab.db')#, isolation_level=None)
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

        for F in (StartPage, Board, ResultsPage):

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

        label = tk.Label(self, text="VisLab", font=LARGE_FONT)
        label.grid(row=0,column=1)
 
        button = tk.Button(self, text="Experiment board",
                            command=lambda: controller.show_frame(Board))
        button.grid(row=1,column=0)

        button2 = tk.Button(self, text="Results Dashboard",
                            command=lambda: controller.show_frame(ResultsPage))
        button2.grid(row=1,column=1)

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

        existing_experiments_qry = "SELECT * FROM experiments"
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
        lineChart_frame.grid(row=2,column=0)
        lineChart_label = tk.Label(lineChart_frame,text="" ,anchor=tk.E)
        lineChart_label.grid(row=0, column=1)
        
        lineChart_svar = tk.StringVar()
        lineChart_svar.set('Select a experiment')
        lineChart_cbbox = ttk.Combobox(lineChart_frame, width=5,textvariable=str(lineChart_svar),state='readonly')
        lineChart_cbbox['values'] = list(existing_experiments['id'])
        lineChart_cbbox.bind('<<ComboboxSelected>>', lambda e: self.plotLinechart(eventObject = e)) 
        lineChart_cbbox.grid(row=3,column=1)

        self.lineChart_plot = Figure(figsize=(4,4), dpi=100)
        self.lineChart_subplot = self.lineChart_plot.add_subplot(111)

        self.lineChart_canvas = FigureCanvasTkAgg(self.lineChart_plot, lineChart_frame) 
        self.lineChart_canvas.draw()
        self.lineChart_canvas._tkcanvas.grid(row=3,column=0)
        lineChart_tframe = tk.Frame(lineChart_frame)
        lineChart_tframe.grid(row=4,column=0)
        lineChart_toolbar = NavigationToolbar2Tk(self.lineChart_canvas,lineChart_tframe)

        #Scatter chart
        
        scatterChart_frame = tk.Frame(self.frame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        scatterChart_frame.grid(row=3,column=0)
        scatterChart_label = tk.Label(scatterChart_frame,text="" ,anchor=tk.E)
        scatterChart_label.grid(row=0, column=1)        
        scatterChart_svar = tk.StringVar()
        scatterChart_svar.set('Select a experiment')
        scatterChart_cbbox = ttk.Combobox(scatterChart_frame, width=5,textvariable=str(scatterChart_svar),state='readonly')
        scatterChart_cbbox['values'] = list(existing_experiments['id'])
        scatterChart_cbbox.bind('<<ComboboxSelected>>', lambda e: self.plotScatterchart(eventObject = e)) 
        scatterChart_cbbox.grid(row=3,column=1)

        self.scatterChart_plot = Figure(figsize=(3,3), dpi=100)
        self.scatterChart_subplot = self.scatterChart_plot.add_subplot(111)

        self.scatterChart_canvas = FigureCanvasTkAgg(self.scatterChart_plot, scatterChart_frame) 
        self.scatterChart_canvas.draw()
        self.scatterChart_canvas._tkcanvas.grid(row=3,column=0)
        scatterChart_tframe = tk.Frame(scatterChart_frame)
        scatterChart_tframe.grid(row=4,column=0)
        scatterChart_toolbar = NavigationToolbar2Tk(self.scatterChart_canvas,scatterChart_tframe)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def plotLinechart(self,eventObject): #function that plots the line chart getting input from lineChart_cbbox
        
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
            self.lineChart_plot.subplots_adjust(right=0.74) #adjust legend problem here!



        '''
        second_p = tk.Label(second_p_frame,text="Add second parameter to plot" ,anchor=tk.E)
        second_p.grid(row=4, column=1)
        self.p_svar_lvl1 = tk.StringVar()
        self.p_cb_lvl1 = ttk.Combobox(second_p_frame, width=5,textvariable=self.p_svar_lvl1,state='readonly')
        self.p_cb_lvl1.configure(font=('Roboto', 8))
        self.p_cb_lvl1['values'] = list(others)
        self.p_cb_lvl1.bind('<<ComboboxSelected>>', lambda e: self.changeGraph_1(eventObject=e, exp=exp))
        self.p_cb_lvl1.grid(sticky = tk.W,row=5, column=1)


        self.p_svar_lvl2 = tk.StringVar()
        self.p_cb_lvl2 = ttk.Combobox(second_p_frame, width=5,textvariable=self.p_svar_lvl2,state='readonly')
        self.p_cb_lvl2.configure(font=('Roboto', 8))
        self.p_cb_lvl2['values'] = list(others)
        self.p_cb_lvl2.bind('<<ComboboxSelected>>', lambda e: self.changeGraph_1(eventObject=e, exp=exp))
        self.p_cb_lvl2.grid(sticky = tk.W,row=5, column=2)
 
        self.p_select_svar = tk.StringVar()
        self.p_select_svar.set('Select a parameter to CI plot')
        self.p_select_cb = ttk.Combobox(second_p_frame, width=15,textvariable=self.p_select_svar,state='readonly')
        self.p_select_cb.configure(font=('Roboto', 8))
        self.p_select_cb['values'] = list(self.simulation_runs.loc[self.simulation_runs['experiment'] == exp].drop_duplicates(subset='parameter_name')['parameter_name'])
        self.p_select_cb.bind('<<ComboboxSelected>>', lambda e: self.chooseParameter(eventObject=e, exp=exp))
        self.p_select_cb.grid(sticky = tk.W,row=6, column=1)

        self.line_plot = Figure(figsize=(3,3), dpi=100)
        self.line_subplot = self.line_plot.add_subplot(111)
        #y_data = list(self.results_df.loc[self.results_df['experiment']==exp]['perf_measure_value'])
        #x_data = range(len(y_data))
        #self.line_subplot.plot(x_data,y_data)

        self.t1_plot_canvas = FigureCanvasTkAgg(self.line_plot, self) 
        self.t1_plot_canvas.draw()
        self.t1_plot_canvas._tkcanvas.grid(row=3,column=1)
        toolbarframe_t1 = tk.Frame(self) 
        toolbarframe_t1.grid(row=4,column=1)
        t1_toolbar = NavigationToolbar2Tk(self.t1_plot_canvas,toolbarframe_t1)
        t1_toolbar.update()        
        self.t1_plot_canvas.get_tk_widget().grid(row=3,column=1,sticky = tk.W)

        self.scatter_plot = Figure(figsize=(3,3), dpi=100)
        self.scatter_subplot = self.scatter_plot.add_subplot(111)
        self.t2_plot_canvas = FigureCanvasTkAgg(self.scatter_plot, self) 
        self.t2_plot_canvas.draw()
        self.t2_plot_canvas._tkcanvas.grid(row=3,column=2)
        toolbarframe_t2 = tk.Frame(self) 
        toolbarframe_t2.grid(row=4,column=2)
        t2_toolbar = NavigationToolbar2Tk(self.t2_plot_canvas,toolbarframe_t2)
        t2_toolbar.update()        
        self.t2_plot_canvas.get_tk_widget().grid(row=3,column=2,sticky = tk.W)

        self.ciplot = Figure(figsize=(3,3), dpi=100)
        self.ciplot_subplot = self.ciplot.add_subplot(111)
        self.ciplot_canvas = FigureCanvasTkAgg(self.ciplot, self)
        self.ciplot_canvas.draw()
        self.ciplot_canvas._tkcanvas.grid(row=5, column=1)
        toolbarframe_ciplot = tk.Frame(self)
        toolbarframe_ciplot.grid(row=7, column=1)
        ciplot_toolbar = NavigationToolbar2Tk(self.ciplot_canvas, toolbarframe_ciplot)
        ciplot_toolbar.update()
        self.ciplot_canvas.get_tk_widget().grid(row=6,column=1) 

        #multi variable layout
        mult_v_label = tk.Label(self,text="Multi variable analysis" ,anchor=tk.CENTER)
        mult_v_label.grid(row=1, column=4)

        self.mv_select1_svar = tk.StringVar()
        self.mv_select1_svar.set('Select first parameter to plot')
        self.mv_select1_cb = ttk.Combobox(self, width=15,textvariable=self.mv_select1_svar,state='readonly')
        self.mv_select1_cb.configure(font=('Roboto', 8))
        self.mv_select1_cb['values'] = list(self.simulation_runs.loc[self.simulation_runs['experiment'] == exp].drop_duplicates(subset='parameter_name')['parameter_name'])
        self.mv_select1_cb.bind('<<ComboboxSelected>>', lambda e: self.graph3D(eventObject=e, exp=exp))
        self.mv_select1_cb.grid(sticky = tk.W,row=3, column=5)

        self.mv_select2_svar = tk.StringVar()
        self.mv_select2_svar.set('Select another parameter to plot')
        self.mv_select2_cb = ttk.Combobox(self, width=15,textvariable=self.mv_select2_svar,state='readonly')
        self.mv_select2_cb.configure(font=('Roboto', 8))
        self.mv_select2_cb['values'] = list(self.simulation_runs.loc[self.simulation_runs['experiment'] == exp].drop_duplicates(subset='parameter_name')['parameter_name'])
        self.mv_select2_cb.bind('<<ComboboxSelected>>', lambda e: self.graph3D(eventObject=e, exp=exp))
        self.mv_select2_cb.grid(sticky = tk.W,row=3, column=6)

        self.line3dplt = Figure(figsize=(3,3), dpi=100)
        self.line3dplt_canvas = FigureCanvasTkAgg(self.line3dplt, self)
        self.line3dplt_canvas.draw()
        self.line3dplt_canvas._tkcanvas.grid(row=2, column=4)
        toolbarframe_3dlineplt = tk.Frame(self)
        toolbarframe_3dlineplt.grid(row=4, column=4)
        line3dplt_toolbar = NavigationToolbar2Tk(self.line3dplt_canvas, toolbarframe_3dlineplt)
        line3dplt_toolbar.update()
        self.line3dplt_canvas.get_tk_widget().grid(row=3,column=4,sticky = tk.W)
        self.line3dplt_subplot = self.line3dplt.add_subplot(111,projection='3d')
        '''


    def chooseParameter(self,eventObject, exp):

        p_name = str(eventObject.widget.get())   

        mean = self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_name']==p_name)].groupby('parameter_value').mean()['results']
        std = self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_name']==p_name)].groupby('parameter_value').std()['results']
        category = mean.index
        n = self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_name']==p_name)].count()
        ci = (1.96/np.sqrt(n)) * std
        print(n)
        print('mean')
        print(mean)
        print('std')
        print(std)
        print('category')
        print(category)
        self.ciplot_subplot.errorbar(category, mean, xerr=0.1, yerr = ci, linestyle='',capsize=5)
        self.ciplot_subplot.set_ylabel(str(self.datapoints_df.loc[self.datapoints_df['experiment']==int(exp)]['perf_measure'].item()))
        self.ciplot_subplot.set_xlabel('%s value' % (p_name))
        self.ciplot_subplot.set_title(p_name)
        self.ciplot_canvas.draw()
        #TODO formatar ci plot

    def changeGraph_1(self, eventObject, exp):
        
        #line chart
        p_lvl = eventObject.widget.get()        
        print(p_lvl)
        y_data_l = list(self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_value']==float(p_lvl))]['results'])
        x_data_l = range(len(y_data_l))

        print(y_data_l)
        print(x_data_l)

        self.line_subplot.plot(x_data_l,y_data_l)
        self.line_subplot.set_title(str(list(self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_value']==float(p_lvl))]['parameter_name'])[0]))
        self.line_subplot.set_ylabel(str(self.datapoints_df.loc[self.datapoints_df['experiment']==int(exp)]['perf_measure'].item()))
        self.line_subplot.set_xlabel('Simulation Run')
        self.t1_plot_canvas.draw()

        #scatter plot
        p_lvl1_s = self.p_cb_lvl1.get()
        p_lvl2_s = self.p_cb_lvl2.get()

        if p_lvl1_s != None or p_lvl2_s != None:

            y_data_s = list(self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_value']==float(p_lvl1_s))]['results'])
            x_data_s = list(self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_value']==float(p_lvl2_s))]['results'])
            self.scatter_subplot.scatter(x_data_s,y_data_s)
            parameter_name = str(list(self.simulation_runs.loc[(self.simulation_runs['experiment']==int(exp)) & (self.simulation_runs['parameter_value']==float(p_lvl))]['parameter_name'])[0])
            parameter_value_l = str(p_lvl1_s)
            parameter_value_h = str(p_lvl2_s)
            self.scatter_subplot.set_title(parameter_name)
            self.scatter_subplot.set_ylabel(str(self.datapoints_df.loc[self.datapoints_df['experiment']==int(exp)]['perf_measure'].item() + '  %s = %s' %(parameter_name,parameter_value_l)))
            self.scatter_subplot.set_xlabel(str(self.datapoints_df.loc[self.datapoints_df['experiment']==int(exp)]['perf_measure'].item() + '  %s = %s' %(parameter_name,parameter_value_h)))

            self.t2_plot_canvas.draw()

        #TODO implementar outros gráficos

    def graph3D(self, eventObject, exp):

        p1 = self.mv_select1_cb.get()
        p2 = self.mv_select2_cb.get()

        x = self.simulation_runs.loc[(self.simulation_runs['experiment']==exp) & (self.simulation_runs['parameter_name']==p1)]['parameter_value']
        print(x)
        #x = [1,2,3,4]
        y = self.simulation_runs.loc[(self.simulation_runs['experiment']==exp) & (self.simulation_runs['parameter_name']==p2)]['parameter_value']
        print(y)
        #y=[8,7,6,4]
        z = self.simulation_runs.loc[(self.simulation_runs['experiment']==exp) & (self.simulation_runs['parameter_name']==p2)]['results']
        print(z)
        #z = [123,13,3,4]
        self.line3dplt_subplot.plot(x,y,z)
        self.line3dplt_canvas.draw()



app = SeaofBTCapp()
app.geometry("1920x1080")    
app.mainloop()