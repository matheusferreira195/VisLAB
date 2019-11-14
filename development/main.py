# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:05:28 2019
@author: mathe
"""
import tkinter as tk
import sqlite3
import pandas as pd
import math
from statistics import mean
from scipy import stats
from tkinter import ttk
from tkinter import messagebox
from generate_dcdf import generate_dcdf
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
from random import random
import random
from statistics import mean
from random import randrange, uniform
import sys,os
from tkinter import filedialog

sys.path.append(os.path.realpath('..'))

#loading assets
NORM_FONT= ("Segoe UI", 10)
NORM_FONT_BOLD= ("Segoe UI Bold", 20)
LARGE_FONT = ("Roboto", 20)
WELCOME_FONT = ("Segoe UI", 60)
path = os.path.realpath('..')+r'\VisLab'
#Database connection and set up
print(path)
cnx = sqlite3.connect(path + r'\resources\vislab.db')#, isolation_level=None)
gaCnx = sqlite3.connect(path + r'\resources\ga.db')

sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))

cursor = cnx.cursor()
cursorGA = gaCnx.cursor()

backgroundColor1 = '#202126'
backgroundColor2 = '#3d68d5'

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
    path_p = os.path.dirname(path)
    mers = [f for f in glob.glob(path_p + "**/*.mer", recursive=True)]
    lsas = [f for f in glob.glob(path_p + "**/*.lsa", recursive=True)]
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
            #print(df)
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
            else:
                pass
                #print('erro df.empty')
    return headway_mean 
    
        
def vissim_simulation(experiment, Vissim, default = 0):

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
                            #print('problema')
                            result = calculate_shdwy(vissimFile, dc_data['dc_number'].item, replication) 
                            
                        else:
                           # print(dc_data['time_p'])
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
                    

                    for p_name,p_value in dc_data.iteritems():

                        seedDb = seed + replication*seed_inc

                        cursor.execute("UPDATE simulation_runs SET results = %s WHERE experiment = %s AND parameter_name = '%s' AND parameter_value = %s AND seed = %s" % (result,experiment,'default','default',seedDb))
                        cnx.commit()
    else:

        Vissim.Simulation.SetAttValue('RandSeed', seed)
        Vissim.Simulation.SetAttValue('NumRuns', runs)

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

                Vissim.Net.DrivingBehaviors[0].SetAttValue(parameter_name,parameter_df_)

            Vissim.Simulation.SetAttValue('RandSeed', seed)
            Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
            Vissim.Simulation.RunContinuous() #Iniciando Simulação 
            #print('running')

            for index, dc_data in selected_datapts.iterrows(): #Collects perf_measure data
                
                for replication in range(1,runs+1):
                    
                    if dc_data['dc_type'] == 'Data Collector':

                        if dc_data['perf_measure'] == 'Saturation Headway':
                            #print('problema')
                            #A função ja tem replication handling
                            result = calculate_shdwy(vissimFile, dc_data['dc_number'], replication) 
                            
                        else:
                            #print(dc_data['time_p'])
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
                    
                    #print(row)
                    #print('\n')

                    for p_name,p_value in row.iteritems():

                        seedDb = seed + replication*seed_inc

                        cursor.execute("UPDATE simulation_runs SET results = %s WHERE experiment = %s AND parameter_name = '%s' AND parameter_value = %s AND seed = %s" % (result,experiment,p_name,p_value,seedDb))
                        cnx.commit()
        Vissim = None 
 
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

        firstFrame = tk.Frame(self, background=backgroundColor1)
        firstFrame.pack(side=tk.LEFT,fill=tk.Y)

        self.welcomeLabel = tk.Label(firstFrame,text='Vislab', font = WELCOME_FONT,background=backgroundColor1,fg='white')
        self.welcomeLabel.grid(row=0,column=0,sticky='w',padx=50,pady=(100,0))
        self.calPhoto = tk.PhotoImage(file = path + r"\resources\ga.png")  #https://www.flaticon.com/packs/science-121
        self.saPhoto = tk.PhotoImage(file = path + r"\resources\sa.png")
        self.flaskPhoto = tk.PhotoImage(file = path + r"\resources\flask.png")
        self.folderPhoto = tk.PhotoImage(file = path + r"\resources\folder.png")
        self.emptyVideo1 = tk.PhotoImage(file = path + r"\resources\video1.png")
        self.emptyVideo2 = tk.PhotoImage(file = path + r"\resources\video2.png")

        button = tk.Button(firstFrame, text="   Experiment board",
                            command=lambda: controller.show_frame(Board),image=self.flaskPhoto,background=backgroundColor1, highlightthickness = 0, bd = 0,compound="left",fg='white')
        button.grid(row=1,column=0,pady=(50,0),padx=50,sticky='w')

        button2 = tk.Button(firstFrame, text="   Results Dashboard",
                            command=lambda: controller.show_frame(ResultsPage),image=self.saPhoto,background=backgroundColor1, highlightthickness = 0, bd = 0,compound="left",fg='white')
        button2.grid(row=2,column=0,pady=5,padx=50,sticky='w')

        button2 = tk.Button(firstFrame, text="   Calibration",
                            command=lambda: controller.show_frame(CalibrationPage),image=self.calPhoto,background=backgroundColor1, highlightthickness = 0, bd = 0,compound="left",fg='white')
        button2.grid(row=3,column=0,pady=5,padx=50,sticky='w')

        button3 = tk.Button(firstFrame, text="   Open Vissim net file (.ipnx)",
                            command= self.openFile,image=self.folderPhoto,background=backgroundColor1, highlightthickness = 0, bd = 0,compound="left",fg='white')
        button3.grid(row=4,column=0,pady=5,padx=50,sticky='w')

        secondFrame = tk.Frame(self, background=backgroundColor2)
        secondFrame.pack(fill=tk.BOTH,side=tk.RIGHT,expand=True)

        labelVideo1 = tk.Label(secondFrame,text='Welcome tutorial', font=NORM_FONT,background=backgroundColor2,fg='black',compound='top',image=self.emptyVideo1,anchor='w')
        labelVideo1.grid(row=0,column=0,pady=(50,0),padx=(50),sticky='w')

        minivideosFrame = tk.Frame(secondFrame, background=backgroundColor2)
        minivideosFrame.grid(row=1,column=0,pady=(5,0),sticky='w')

        labelVideo2 = tk.Label(minivideosFrame,text='How to generate reports', font=NORM_FONT,background=backgroundColor2,fg='black',compound='top',image=self.emptyVideo2,anchor='w')
        labelVideo2.grid(row=1,column=0,pady=(50,0),padx=(50),sticky='w')

        textFrame = tk.Frame(secondFrame, background=backgroundColor2)
        textFrame.grid(row=0,column=1,pady=(50,0),padx=(50),sticky='w')

        labelIntro = tk.Label(textFrame,text='Contribute', font=NORM_FONT_BOLD,background=backgroundColor2,fg='black',anchor=tk.W, justify=tk.LEFT)
        labelIntro.grid(row=0,column=3,pady=(50,0),padx=(10),sticky='w')

        introtext = "You can contribute with this open project on GitHub:\nhttps://github.com/matheusferreira195/VisLAB"
        introText = tk.Label(textFrame, text=introtext,font=NORM_FONT,background=backgroundColor2,fg='black',borderwidth=0,anchor=tk.W, justify=tk.LEFT)
        introText.grid(row=1,column=3,pady=(5,0),padx=(10),sticky='w')
        
        labelAbout = tk.Label(textFrame,text='Changelog', font=NORM_FONT_BOLD,background=backgroundColor2,fg='black',anchor=tk.W, justify=tk.LEFT)
        labelAbout.grid(row=2,column=3,pady=(5,0),padx=(10),sticky='w')

        abouttext = """0.1.1: We are live!"""
        aboutText = tk.Label(textFrame,text=abouttext, font=NORM_FONT,background=backgroundColor2,fg='black',borderwidth=0,anchor=tk.W, justify=tk.LEFT)
        aboutText.grid(row=3,column=3,pady=(5,0),padx=(10),sticky='w')

    def openFile(self):

            global vissimFile
            global Vissim
            global dc_data
            vissimFile = filedialog.askopenfilename().replace('/','\\')
            #print(vissimFile)
            Vissim = None #com.Dispatch('Vissim.Vissim')
            Vissim = com.Dispatch("Vissim.Vissim") #Abrindo o Vissim
            flag = False 
            Vissim.LoadNet(vissimFile, flag) #Carregando o arquivo'''            
            dc_data = generate_dcdf(Vissim)
            #print(dc_data)
            
parameter_db = pd.read_csv(path + r'\resources\parameters.visdb')       
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
                            command=lambda: controller.show_frame(CalibrationPage))
        button_calibration.grid(row=0,column=2)

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

        button_simulation = tk.Button(self, text = "Simulate", command = lambda: vissim_simulation(exp, Vissim), anchor = tk.W)
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
        
        #print('configurations')
        #print(configurations)

        for i in range(configurations):

            edit_windows(experiment=exp,parent = win, cfg=(i+1),new=1)

        
        #print(self.experiment_data)

    def delete_postit(self,exp):
        #print(self.canvas_l)
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

        self.vsb.pack(side="left", fill="y")
        self.canvas.pack(side="right", fill="both", expand=True)
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
        print(self.simulation_runs)
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

        #difmeans boxplot

        self.difmeansBpFrame = tk.Frame(self.frame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        self.difmeansBpFrame.grid(row=4,column=0)

        self.difmeansBpWidgetFrame = tk.Frame(self.difmeansBpFrame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        self.difmeansBpWidgetFrame.grid(row=0,column=0)

        self.difmeansBpMainLabel = tk.Label(self.difmeansBpWidgetFrame, text="Difference of means test plot", anchor=tk.CENTER)
        self.difmeansBpMainLabel.grid(row=0,column=0)

        self.difmeansBpSvarExpList = []
        self.difmeansBpSvarParList = []

        self.difmeansBpLabel1 = tk.Label(self.difmeansBpWidgetFrame, text="\nFirst Difference: \n", anchor=tk.CENTER)
        self.difmeansBpLabel1.grid(row=1,column=0)
        self.difmeansBpSvar1 = tk.StringVar()
        self.difmeansBpSvar1.set('Select an experiment')
        self.difmeansBpExp1Cbbox = ttk.Combobox(self.difmeansBpWidgetFrame,width=15,textvariable=str(self.difmeansBpSvar1),state='readonly')
        self.difmeansBpExp1Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansBpExp1Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelectPlot(eventObject=e))
        self.difmeansBpExp1Cbbox.grid(row=2,column=0)

        self.difmeansBpSvarp1 = tk.StringVar()
        self.difmeansBpSvarp1.set('Select a param. profile')
        self.difmeansBpCbboxp1 = ttk.Combobox(self.difmeansBpWidgetFrame,width=30,textvariable=str(self.difmeansBpSvarp1),state='readonly')
        self.difmeansBpCbboxp1['values'] = []
        #self.difmeansCbboxp1.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelect(eventObject=e))
        self.difmeansBpCbboxp1.grid(row=2,column=1)
        
        self.difmeansBpSvar2 = tk.StringVar()
        self.difmeansBpSvar2.set('Select an experiment')
        self.difmeansBpExp2Cbbox = ttk.Combobox(self.difmeansBpWidgetFrame,width=15,textvariable=str(self.difmeansBpSvar2),state='readonly')
        self.difmeansBpExp2Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansBpExp2Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelectPlot(eventObject=e))
        self.difmeansBpExp2Cbbox.grid(row=3,column=0)
        
        self.difmeansBpSvarp2 = tk.StringVar()
        self.difmeansBpSvarp2.set('Select a param. profile')
        self.difmeansBpCbboxp2 = ttk.Combobox(self.difmeansBpWidgetFrame,width=30,textvariable=str(self.difmeansBpSvarp2),state='readonly')
        self.difmeansBpCbboxp2['values'] = []
        self.difmeansBpCbboxp2.grid(row=3,column=1,pady=(0,10))

        self.difmeansBpLabel2 = tk.Label(self.difmeansBpWidgetFrame, text="\nSecond Difference: \n", anchor=tk.CENTER)
        self.difmeansBpLabel2.grid(row=4,column=0)        
        self.difmeansBpSvar3 = tk.StringVar()
        self.difmeansBpSvar3.set('Select an experiment')
        self.difmeansBpExp3Cbbox = ttk.Combobox(self.difmeansBpWidgetFrame,width=15,textvariable=str(self.difmeansBpSvar3),state='readonly')
        self.difmeansBpExp3Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansBpExp3Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelectPlot(eventObject=e))
        self.difmeansBpExp3Cbbox.grid(row=5,column=0)

        self.difmeansBpSvarp3 = tk.StringVar()
        self.difmeansBpSvarp3.set('Select a param. profile')
        self.difmeansBpCbboxp3 = ttk.Combobox(self.difmeansBpWidgetFrame,width=30,textvariable=str(self.difmeansBpSvarp3),state='readonly')
        self.difmeansBpCbboxp3['values'] = []
        #self.difmeansCbboxp1.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelect(eventObject=e))
        self.difmeansBpCbboxp3.grid(row=5,column=1)


        self.difmeansBpSvar4 = tk.StringVar()
        self.difmeansBpSvar4.set('Select an experiment')
        self.difmeansBpExp4Cbbox = ttk.Combobox(self.difmeansBpWidgetFrame,width=15,textvariable=str(self.difmeansBpSvar4),state='readonly')
        self.difmeansBpExp4Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansBpExp4Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelectPlot(eventObject=e))
        self.difmeansBpExp4Cbbox.grid(row=6,column=0,pady=(0,10))

        self.difmeansBpSvarp4 = tk.StringVar()
        self.difmeansBpSvarp4.set('Select a param. profile')
        self.difmeansBpCbboxp4 = ttk.Combobox(self.difmeansBpWidgetFrame,width=30,textvariable=str(self.difmeansBpSvarp4),state='readonly')
        self.difmeansBpCbboxp4['values'] = []
        self.difmeansBpCbboxp4.grid(row=6,column=1)

        self.difmeansBpLabel3 = tk.Label(self.difmeansBpWidgetFrame, text="\nThird Difference: \n", anchor=tk.CENTER)
        self.difmeansBpLabel3.grid(row=7,column=0)
        self.difmeansBpSvar5 = tk.StringVar()
        self.difmeansBpSvar5.set('Select an experiment')
        self.difmeansBpExp5Cbbox = ttk.Combobox(self.difmeansBpWidgetFrame,width=15,textvariable=str(self.difmeansBpSvar5),state='readonly')
        self.difmeansBpExp5Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansBpExp5Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelectPlot(eventObject=e))
        self.difmeansBpExp5Cbbox.grid(row=8,column=0)

        self.difmeansBpSvarp5 = tk.StringVar()
        self.difmeansBpSvarp5.set('Select a param. profile')
        self.difmeansBpCbboxp5 = ttk.Combobox(self.difmeansBpWidgetFrame,width=30,textvariable=str(self.difmeansBpSvarp5),state='readonly')
        self.difmeansBpCbboxp5['values'] = []
        #self.difmeansCbboxp1.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelect(eventObject=e))
        self.difmeansBpCbboxp5.grid(row=8,column=1)

        self.difmeansBpSvar6 = tk.StringVar()
        self.difmeansBpSvar6.set('Select an experiment')
        self.difmeansBpExp6Cbbox = ttk.Combobox(self.difmeansBpWidgetFrame,width=15,textvariable=str(self.difmeansBpSvar6),state='readonly')
        self.difmeansBpExp6Cbbox['values'] = list(existing_experiments['id'])
        self.difmeansBpExp6Cbbox.bind('<<ComboboxSelected>>', lambda e: self.difmeanSelectPlot(eventObject=e))
        self.difmeansBpExp6Cbbox.grid(row=9,column=0)

        self.difmeansBpSvarp6 = tk.StringVar()
        self.difmeansBpSvarp6.set('Select a param. profile')
        self.difmeansBpCbboxp6 = ttk.Combobox(self.difmeansBpWidgetFrame,width=30,textvariable=str(self.difmeansBpSvarp6),state='readonly')
        self.difmeansBpCbboxp6['values'] = []
        self.difmeansBpCbboxp6.grid(row=9,column=1)
        self.genButton = ttk.Button(self.difmeansBpWidgetFrame,text='Plot', command= self.difmeanPlot)
        self.genButton.grid(row=10,column=0,pady=10,padx= 50)

        #putting svars in lists to iterate later
        self.difmeansBpSvarExpList1 = []
        self.difmeansBpSvarParList1 = []
        self.difmeansBpSvarExpList2 = []
        self.difmeansBpSvarParList2 = []
        self.difmeansBpSvarExpList3 = []
        self.difmeansBpSvarParList3 = []

        self.difmeansBpSvarExpList1.append(self.difmeansBpSvar1)        
        self.difmeansBpSvarExpList1.append(self.difmeansBpSvar2)
        self.difmeansBpSvarParList1.append(self.difmeansBpSvarp1)
        self.difmeansBpSvarParList1.append(self.difmeansBpSvarp2)

        self.difmeansBpSvarExpList2.append(self.difmeansBpSvar3)
        self.difmeansBpSvarExpList2.append(self.difmeansBpSvar4)
        self.difmeansBpSvarParList2.append(self.difmeansBpSvarp3)        
        self.difmeansBpSvarParList2.append(self.difmeansBpSvarp4)

        self.difmeansBpSvarExpList3.append(self.difmeansBpSvar5)
        self.difmeansBpSvarExpList3.append(self.difmeansBpSvar6)
        self.difmeansBpSvarParList3.append(self.difmeansBpSvarp5)        
        self.difmeansBpSvarParList3.append(self.difmeansBpSvarp6)

        self.difmeansBpSvarExpMetaList = [self.difmeansBpSvarExpList1, self.difmeansBpSvarExpList2, self.difmeansBpSvarExpList3]
        self.difmeansBpSvarParMetaList = [self.difmeansBpSvarParList1, self.difmeansBpSvarParList2, self.difmeansBpSvarParList3]

        #difmeans plot

        self.difmeansBpPlotFrame = tk.Frame(self.difmeansBpFrame)
        self.difmeansBpPlotFrame.grid(row=0,column=1)
  
        self.difmeansBpPlotFigure = Figure(figsize=(5,4), dpi=100)
        self.difmeansBpPlotSubplot = self.difmeansBpPlotFigure.add_subplot(111)
        self.difmeansBpPlotCanvas = FigureCanvasTkAgg(self.difmeansBpPlotFigure, self.difmeansBpPlotFrame)
        self.difmeansBpPlotCanvas.draw()
        self.difmeansBpPlotCanvas._tkcanvas.grid(row=0,column=0)
        self.difmeansBpPlotTFrame = tk.Frame(self.difmeansBpPlotFrame)
        self.difmeansBpPlotTFrame.grid(row=1,column=0)
        self.difmeansBpPlotToolbar = NavigationToolbar2Tk(self.difmeansBpPlotCanvas, self.difmeansBpPlotTFrame)

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

    def difmeanSelectPlot(self, eventObject):

        #print(eventObject.widget)

        index_cbbx = self.difmeansBpWidgetFrame.winfo_children().index(eventObject.widget)
        #print(index_cbbx)
        #print(self.difmeansBpWidgetFrame.winfo_children())

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

        self.difmeansBpWidgetFrame.winfo_children()[index_cbbx+1]['values'] = labelTxt_ls

    def difmeanPlot(self):
        
        self.difmeansBpPlotSubplot.cla()
        xs=[]
        ys=[]
        Es=[]
        labels =[]

        for i in range(3):

            #print(i)
            difExp = self.difmeansBpSvarExpMetaList[i]
            difPar = self.difmeansBpSvarParMetaList[i]
            #data
            exp1 = difExp[0].get()
            par1 = self.cfgsDict[difPar[0].get()]
            exp2 = difExp[1].get()
            par2 = self.cfgsDict[difPar[1].get()]
            print(exp1)
            dados_1 = pd.read_sql('select * from simulation_runs where experiment = %s and sim_perf = %s' % (exp1,par1),cnx)['results'].drop_duplicates()
            dados_2 = pd.read_sql('select * from simulation_runs where experiment = %s and sim_perf = %s' % (exp2,par2),cnx)['results'].drop_duplicates()

            #Analysis
            linreg = stats.linregress(dados_1, dados_2)            
            mean1 = dados_1.mean()
            mean2 = dados_2.mean()
            difmean = mean1-mean2
            n1 = dados_1.count()
            n2 = dados_2.count()
            n = min(n1,n2)
            var1 = dados_1.std()**2
            var2 = dados_2.std()**2
            r_values = stats.pearsonr(dados_1,dados_2)
            r = r_values[0]
            r_p = r_values[1]
            df = n-1
            statt = stats.ttest_rel(dados_1,dados_2)

            if r_p < 0.05:
                #dependent

                difData = dados_1 - dados_2
                difData_std = difData.std()
                talfa = stats.t.ppf(0.975, df)
                difData_n = difData.count()
                mean = difData.mean() #mean of differences
                E = talfa*(difData_std/np.sqrt(difData_n))

                tp = 'Paired'
                
            else:
                #independent
                talfa = stats.t.ppf(0.975, df)
                stdn1 = var1/n1
                stdn2 = var2/n2
                mean = difmean #difference of means

                E = talfa*np.sqrt(stdn1+stdn2)

                tp = 'Independent'
            #print(tp)
            x = i#list(labels)
            y = mean
            e = E
            xs.append(x)
            ys.append(y)
            Es.append(E)
            labels.append('%sº difference\n %s' % (i+1,tp))

        self.difmeansBpPlotSubplot.set_ylabel(list(self.datapoints_df.loc[self.datapoints_df['experiment']==(int(exp1))]['perf_measure'].drop_duplicates()))   
        self.difmeansBpPlotSubplot.errorbar(labels, ys, yerr=Es, fmt='s',capsize=5)
        self.difmeansBpPlotSubplot.set_xticklabels(labels,rotation=45,fontsize=8)
        self.difmeansBpPlotFigure.tight_layout()        
        self.difmeansBpPlotCanvas.draw()

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
        r = linreg.rvalue
        print(r)
        #self.scatterChart_subplot.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.,prop={'size': 8})
        #self.scatterChart_subplot.text(x_data[0], y_data[0], 'R-squared = %0.2f' % r_squared)
        anchored_text = matplotlib.offsetbox.AnchoredText('R = %0.2f \n P-value = %0.2f' % (r,linreg.pvalue), loc=4, prop = dict(fontsize=8))
        
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

        #dc_data = generate_dcdf_test()
        parameter_db = pd.read_csv(r'E:\Google Drive\Scripts\VisLab\resources\parameters.visdb') 
        self.runPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\power.png")  #https://www.flaticon.com/packs/science-121
        self.cfgPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\settings.png")
        self.resultsPhoto = tk.PhotoImage(file = r"E:\Google Drive\Scripts\VisLab\resources\results.png")
        
        label = tk.Label(frame, text="Calibration", font=LARGE_FONT)
        label.grid(row=0,column=1)

        runLabel = tk.Label(frame, text="Run calibration")
        runLabel.grid(row=1,column=2)
        runButton = tk.Button(frame, text="Run calibration",
                            command=lambda: self.whichPreset(),image=self.runPhoto)
        runButton.grid(row=2,column=2)

        cfgLabel = tk.Label(frame, text="Config calibration")
        cfgLabel.grid(row=1,column=1)
        cfgButton = tk.Button(frame, text="Config calibration",
                            command=lambda: self.cfgCalibration(),image=self.cfgPhoto)
        cfgButton.grid(row=2,column=1)

        resultsLabel = tk.Label(frame, text="Results calibration")
        resultsLabel.grid(row=1,column=3)        
        resultsButton = tk.Button(frame, text="Results calibration",
                            command=lambda: self.resultsCalibration(),image=self.resultsPhoto)
        resultsButton.grid(row=2,column=3)
    
    def whichPreset(self):
        backgroundColor1 = '#202126'
        self.presets = pd.read_sql("SELECT * FROM configurationsGA",gaCnx)

        self.askingWindow = tk.Toplevel()
        self.askingWindow.configure(bg=backgroundColor1)
        self.askingWindow.wm_title("Select a calibration preset")

        self.askLabel = tk.Label(self.askingWindow, text="Select a preset to start the calibration: ", background=backgroundColor1,fg='white', font =NORM_FONT)
        self.askLabel.grid(row=0,column=0,sticky='w')

        self.cbboxSvar = tk.StringVar()
        self.askCbbox = ttk.Combobox(self.askingWindow, textvariable = self.cbboxSvar)
        self.askCbbox['values'] = list(self.presets['name'])
        self.askCbbox.grid(row=0,column=1)

        self.selectedButton = tk.Button(self.askingWindow, text = 'Ok', command=lambda: runCalibration(name=self.cbboxSvar.get()),background=backgroundColor1, highlightthickness = 0, bd = 0,compound="left",fg='white')
        self.selectedButton.grid(row=1,column=0)

    def cfgCalibration(self):
        
        s = ttk.Style()
        s.configure('TCombobox', background='white')

        self.presets = pd.read_sql("SELECT * FROM configurationsGA",gaCnx)

        self.cfgGAWindow = tk.Toplevel()
        self.cfgGAWindow.wm_title("Genetic Algorithm configuration")
        
        self.cfgGAMasterFrame = tk.Frame(self.cfgGAWindow)
        self.cfgGAMasterFrame.grid(row=0,column=0)

        self.cfgGALabel = tk.Label(self.cfgGAMasterFrame, text="Config calibration")
        self.cfgGALabel.pack(pady=15,anchor=tk.W)

        self.selectCfgFrame = tk.Frame(self.cfgGAMasterFrame)
        self.selectCfgFrame.pack(fill=tk.X)
        self.selectCfgLabel = tk.Label(self.selectCfgFrame, text="Select saved config preset: ")
        self.selectCfgLabel.grid(row=0,column=0)
        self.selectCfgSvar = tk.StringVar()
        self.selectCfgCbbox = ttk.Combobox(self.selectCfgFrame, width=5,textvariable=self.selectCfgSvar,state='readonly')
        self.selectCfgCbbox['values'] = list(self.presets['name'].drop_duplicates())
        self.selectCfgCbbox.bind('<<ComboboxSelected>>', lambda e: self.presetSelect(eventObject=e))
        self.selectCfgCbbox.configure(font=('Roboto', 8))
        self.selectCfgCbbox.grid(row=0,column=1)
        self.selectCfgLabel2 = tk.Label(self.selectCfgFrame, text="(don't select if you want start a new one)")
        self.selectCfgLabel2.grid(row=0,column=3)

        self.nameGAFrame = tk.Frame(self.cfgGAMasterFrame)
        self.nameGAFrame.pack(fill=tk.X)
        self.nameGASvar = tk.StringVar()
        self.nameGALabel = tk.Label(self.nameGAFrame, text="Preset name: ")
        self.nameGALabel.grid(row=1,column=0,sticky='w')
        self.nameGAEntry = tk.Entry(self.nameGAFrame,textvariable=self.nameGASvar)
        self.nameGAEntry.grid(row=1,column=1,sticky='w')
        self.separator1h = ttk.Separator(self.cfgGAMasterFrame, orient="horizontal")
        self.separator1h.pack(fill=tk.X,pady=10)#grid(row=2,column=0,sticky='we',columnspan=100)

        self.genGAFrame = tk.Frame(self.cfgGAMasterFrame)
        self.genGAFrame.pack(fill=tk.X)
        self.genGALabel = tk.Label(self.genGAFrame, text="Number of generations: ")
        self.genGALabel.grid(row=3,column=0,sticky='w')
        self.genGASvar = tk.StringVar()
        self.genGAEntry = tk.Entry(self.genGAFrame,textvariable=self.genGASvar)
        self.genGAEntry.grid(row=3,column=1,sticky='w')

        self.indGAFrame = tk.Frame(self.cfgGAMasterFrame)
        self.indGAFrame.pack(fill=tk.X)
        self.indGALabel = tk.Label(self.indGAFrame, text="Number of individuals: ")
        self.indGALabel.grid(row=4,column=0,sticky='w')
        self.indGASvar = tk.StringVar()
        self.indGAEntry = tk.Entry(self.indGAFrame, textvariable=self.indGASvar)
        self.indGAEntry.grid(row=4,column=1,sticky='w')

        self.repGAFrame = tk.Frame(self.cfgGAMasterFrame)
        self.repGAFrame.pack(fill=tk.X)
        self.repGALabel = tk.Label(self.repGAFrame, text="Number of replications: ")
        self.repGALabel.grid(row=5,column=0,sticky='w')
        self.repGASvar = tk.StringVar()
        self.repGAEntry = tk.Entry(self.repGAFrame,textvariable=self.repGASvar)
        self.repGAEntry.grid(row=5,column=1,sticky='w')
        self.separator2h = ttk.Separator(self.cfgGAMasterFrame, orient="horizontal")
        self.separator2h.pack(fill=tk.X,pady=10)

        self.dp_nameGAFrame = tk.Frame(self.cfgGAMasterFrame)
        self.dp_nameGAFrame.pack(fill=tk.X)
        self.dp_nameGALabel = tk.Label(self.dp_nameGAFrame, text="Data Point: ")
        self.dp_nameGALabel.grid(row=8,column=0,sticky='w')
        self.dp_nameGASvar = tk.StringVar()
        self.dp_nameGACbbox = ttk.Combobox(self.dp_nameGAFrame, width=25,textvariable=self.dp_nameGASvar,state='readonly')
        self.dp_nameGACbbox['values'] = list(dc_data['Display'])
        self.dp_nameGACbbox.bind('<<ComboboxSelected>>', lambda e: self.datapointSelect(eventObject=e))
        self.dp_nameGACbbox.configure(font=('Roboto', 8))
        self.dp_nameGACbbox.grid(row=8,column=1)

        self.perfmeasureFrame = tk.Frame(self.cfgGAMasterFrame,bg='white')
        self.perfmeasureFrame.pack(fill=tk.X)
        self.perfmeasureLabel = tk.Label(self.perfmeasureFrame, text="Perf. measure: ",bg='white')
        self.perfmeasureLabel.grid(row=9,column=0,sticky='w')
        self.perfmeasureSvar = tk.StringVar()
        self.perfmeasuresCbbox = ttk.Combobox(self.perfmeasureFrame,textvariable=self.perfmeasureSvar, width=25,style='TCombobox')
        self.perfmeasuresCbbox['values'] = []
        self.perfmeasuresCbbox.configure(font=('Roboto', 8))
        self.perfmeasuresCbbox.grid(row=9,column=1)

        self.fieldLabel = tk.Label(self.perfmeasureFrame, text="Field value: ")
        self.fieldLabel.grid(row=9,column=2,sticky='w',pady=10)
        self.fieldSvar = tk.StringVar()
        self.fieldEntry = tk.Entry(self.perfmeasureFrame, textvariable=self.fieldSvar)
        self.fieldEntry.grid(row=9,column=3,sticky='w')

        self.parameterCbboxList = []
        self.parameterUpList = []
        self.parameterDownList = []

        self.parameterFrame = tk.Frame(self.cfgGAMasterFrame)
        self.parameterFrame.pack()

        self.parameterCbboxSvar = tk.StringVar()
        self.parameterLabel = tk.Label(self.parameterFrame, text="Parameter: ")
        self.parameterLabel.grid(row=10,column=0,sticky='w')
        self.parameterCbbox = ttk.Combobox(self.parameterFrame,textvariable=self.parameterCbboxSvar, width=25)
        self.parameterCbbox['values'] = list(parameter_db['Identifier'])
        self.parameterCbbox.configure(font=('Roboto', 8))
        self.parameterCbbox.grid(row=10,column=1)
        self.parameterCbboxList.append(self.parameterCbboxSvar)

        self.parameterDownSvar = tk.StringVar()
        self.parameterDownLabel = tk.Label(self.parameterFrame, text="Bottom limit: ")
        self.parameterDownLabel.grid(row=10,column=2,sticky='w',padx=5)
        self.parameterDown = tk.Entry(self.parameterFrame,textvariable = self.parameterDownSvar)
        self.parameterDown.grid(row=10,column=3,sticky='w')
        self.parameterDownList.append(self.parameterDownSvar)

        self.parameterUpSvar = tk.StringVar()
        self.parameterUpLabel = tk.Label(self.parameterFrame, text="Upper limit: ")
        self.parameterUpLabel.grid(row=10,column=4,sticky='w',padx=5)
        self.parameterUp = tk.Entry(self.parameterFrame,textvariable = self.parameterUpSvar)
        self.parameterUp.grid(row=10,column=5,sticky='w')
        self.parameterUpList.append(self.parameterUpSvar)

        self.addParameterButton = tk.Button(self.parameterFrame,text='+ Parameter')
        self.addParameterButton.bind("<Button-1>",lambda e: self.addParameter(eventObject=e))
        self.addParameterButton.grid(row=11,column=1)

        self.cfgGAWindow.protocol("WM_DELETE_WINDOW", self.onClose)

    def presetSelect(self,eventObject):

        selected = self.selectCfgSvar.get()
        
        if len(selected) != 0:
            
            self.parameterFrame.destroy()

            del(self.parameterUpList[0])
            del(self.parameterDownList[0])
            del(self.parameterCbboxList[0])

            dataSelected = self.presets.loc[self.presets['name']==selected].reset_index(drop=True)
            parametersSelected = pd.read_sql("SELECT * FROM parametersGA WHERE name = '%s'" % selected,gaCnx).reset_index(drop=True)
            
            print(dataSelected)
            print(parametersSelected)

            self.nameGASvar.set(selected)
            self.genGASvar.set(dataSelected['gen'][0])
            self.indGASvar.set(dataSelected['ind'][0])
            self.repGASvar.set(dataSelected['rep'][0])
            self.dp_nameGASvar.set( '#%s / %s' % (dataSelected['datapoint_id'][0],dataSelected['datapoint_type'][0]))
            self.perfmeasureSvar.set(dataSelected['perf_measure'][0])
            self.fieldSvar.set(dataSelected['field_data'][0])
            #print(parametersSelected)

            for index, par in parametersSelected.iterrows():

                #print(index)

                self.parameterFrame = tk.Frame(self.cfgGAMasterFrame)
                self.parameterFrame.pack()    
                    
                self.parameterCbboxSvar = tk.StringVar()
                self.parameterLabel = tk.Label(self.parameterFrame, text="Parameter: ")
                self.parameterLabel.grid(row=10,column=0,sticky='w')
                self.parameterCbbox = ttk.Combobox(self.parameterFrame,textvariable=self.parameterCbboxSvar, width=25)
                self.parameterCbbox['values'] = list(parameter_db['Identifier'])
                self.parameterCbbox.configure(font=('Roboto', 8))
                self.parameterCbbox.grid(row=10,column=1)
                self.parameterCbboxList.append(self.parameterCbboxSvar)

                self.parameterDownSvar = tk.StringVar()
                self.parameterDownLabel = tk.Label(self.parameterFrame, text="Bottom limit: ")
                self.parameterDownLabel.grid(row=10,column=2,sticky='w',padx=5)
                self.parameterDown = tk.Entry(self.parameterFrame,textvariable = self.parameterDownSvar)
                self.parameterDown.grid(row=10,column=3,sticky='w')
                self.parameterDownList.append(self.parameterDownSvar)

                self.parameterUpSvar = tk.StringVar()
                self.parameterUpLabel = tk.Label(self.parameterFrame, text="Upper limit: ")
                self.parameterUpLabel.grid(row=10,column=4,sticky='w',padx=5)
                self.parameterUp = tk.Entry(self.parameterFrame,textvariable = self.parameterUpSvar)
                self.parameterUp.grid(row=10,column=5,sticky='w')
                self.parameterUpList.append(self.parameterUpSvar)
                
                self.parameterCbboxSvar.set(par['parameter_name'])
                self.parameterDownSvar.set(par['parameter_b_value'])
                self.parameterUpSvar.set(par['parameter_u_value'])

                if index == len(parametersSelected.index)-1:

                    self.addParameterButton = tk.Button(self.parameterFrame,text='+ Parameter')
                    self.addParameterButton.bind("<Button-1>",lambda e: self.addParameter(eventObject=e))
                    self.addParameterButton.grid(row=11,column=1)

    def addParameter(self,eventObject):

        eventObject.widget.destroy()

        self.parameterFrame = tk.Frame(self.cfgGAMasterFrame)
        self.parameterFrame.pack()    
               
        self.parameterCbboxSvar = tk.StringVar()
        self.parameterLabel = tk.Label(self.parameterFrame, text="Parameter: ")
        self.parameterLabel.grid(row=10,column=0,sticky='w')
        self.parameterCbbox = ttk.Combobox(self.parameterFrame,textvariable=self.parameterCbboxSvar, width=25)
        self.parameterCbbox['values'] = list(parameter_db['Identifier'])
        self.parameterCbbox.configure(font=('Roboto', 8))
        self.parameterCbbox.grid(row=10,column=1)
        self.parameterCbboxList.append(self.parameterCbboxSvar)

        self.parameterDownSvar = tk.StringVar()
        self.parameterDownLabel = tk.Label(self.parameterFrame, text="Bottom limit: ")
        self.parameterDownLabel.grid(row=10,column=2,sticky='w',padx=5)
        self.parameterDown = tk.Entry(self.parameterFrame,textvariable = self.parameterDownSvar)
        self.parameterDown.grid(row=10,column=3,sticky='w')
        self.parameterDownList.append(self.parameterDownSvar)

        self.parameterUpSvar = tk.StringVar()
        self.parameterUpLabel = tk.Label(self.parameterFrame, text="Upper limit: ")
        self.parameterUpLabel.grid(row=10,column=4,sticky='w',padx=5)
        self.parameterUp = tk.Entry(self.parameterFrame,textvariable = self.parameterUpSvar)
        self.parameterUp.grid(row=10,column=5,sticky='w')
        self.parameterUpList.append(self.parameterUpSvar)

        self.addParameterButton = tk.Button(self.parameterFrame,text='+ Parameter')
        self.addParameterButton.bind("<Button-1>",lambda e: self.addParameter(eventObject=e))
        self.addParameterButton.grid(row=11,column=1)

    def datapointSelect(self,eventObject):

        value = eventObject.widget.get()

        dc_match = dc_data.loc[dc_data['Display'] == value]
        data_point_type = dc_match['Type'].item()
        Dc_Number = dc_match['No'].item()         

        if data_point_type == 'Data Collector':
            self.perfmeasuresCbbox['values'] = ['QueueDelay', 'SpeedAvgArith', 'OccupRate','Acceleration', 'Lenght', 'Vehs', 'Pers','Saturation Headway']

        elif data_point_type == 'Travel Time Collector':
            self.perfmeasuresCbbox['values'] = ['StopDelay', 'Stops', 'VehDelay', 'Vehs', 'Persons Delay', 'Persons']
            
        else:
            self.perfmeasuresCbbox['values'] = ['QLen', 'QLenMax', 'QStops']

    def parameterSelect(self,eventObject):
        pass

    def onClose(self):

        answer = messagebox.askyesnocancel("Exit", "Do you want to save and exit?")

        if answer == True:

            name = self.nameGAEntry.get()

            gen = self.genGAEntry.get()

            ind = self.indGAEntry.get()

            rep = self.repGAEntry.get()

            dp_name = self.dp_nameGASvar.get()
            dc_match = dc_data.loc[dc_data['Display'] == dp_name]
            datapoint_type = dc_match['Type'].item()
            Dc_Number = dc_match['No'].item() 
            print(datapoint_type)
            perf_measure = self.perfmeasureSvar.get()

            field_data = self.fieldSvar.get()

            gaCnx.execute("""INSERT OR REPLACE INTO configurationsGA (name,rep,ind,gen,datapoint_type,datapoint_id,perf_measure,field_data) 
                            VALUES ('%s',%s,%s,%s,'%s',%s,'%s',%s)""" % (name,rep,ind,gen,datapoint_type,Dc_Number,perf_measure,field_data))

            for i in range(len(self.parameterCbboxList)):

                parameter = self.parameterCbboxList[i].get()
                down = self.parameterDownList[i].get()
                up = self.parameterUpList[i].get()
                query = """INSERT OR REPLACE INTO parametersGA (name,parameter_name,parameter_b_value,parameter_u_value)
                                    VALUES ('%s','%s',%s,%s)""" % (name,parameter,down,up)
                print(query)
                gaCnx.execute(query)

            gaCnx.commit()

            self.cfgGAWindow.destroy()

        elif answer == False:

            self.cfgGAWindow.destroy()

        else:

            self.cfgGAWindow.lift()

    def resultsCalibration(self):
        
        self.presets = pd.read_sql("SELECT * FROM configurationsGA",gaCnx)
        self.resultsGAWindow = tk.Toplevel()
        self.resultsGAWindow.wm_title("GA Calibration Results")
        
        self.resultsGAFrame = tk.Frame(self.resultsGAWindow)
        self.resultsGAFrame.grid(row=0,column=0)

        #perf chart section
        self.cbboxLabelFrame = tk.Frame(self.resultsGAFrame)
        self.cbboxLabelFrame.grid(row=0,column=0,sticky='w')
        self.resultsGALabel = tk.Label(self.cbboxLabelFrame, text="GA Calibration results")
        self.resultsGALabel.grid(row=0,column=0,sticky='w')
        
        self.selectCfgLabel = tk.Label(self.cbboxLabelFrame, text="\n Select saved config preset: ")
        self.selectCfgLabel.grid(row=1,column=0,sticky='w')
        self.selectCfgSvar = tk.StringVar()
        self.selectCfgCbbox = ttk.Combobox(self.cbboxLabelFrame, width=5,textvariable=self.selectCfgSvar,state='readonly')
        self.selectCfgCbbox['values'] = list(self.presets['name'].drop_duplicates())
        self.selectCfgCbbox.bind('<<ComboboxSelected>>', lambda e: self.presetSelectResults(eventObject=e))
        self.selectCfgCbbox.configure(font=('Roboto', 8))
        self.selectCfgCbbox.grid(row=1,column=1,sticky='w')

        self.perfChartLabel = tk.Label(self.resultsGAFrame, text="\n Performance: ")
        self.perfChartLabel.grid(row=2,column=0,sticky='w')

        perfChart_frame = tk.Frame(self.resultsGAFrame,highlightbackground="green", highlightcolor="green", highlightthickness=1, width=100, height=100, bd= 0)
        perfChart_frame.grid(row=3,column=0,sticky='w')

        self.perfChart_plot = Figure(figsize=(5,4), dpi=100)
        self.perfChart_subplot = self.perfChart_plot.add_subplot(111)

        self.perfChart_canvas = FigureCanvasTkAgg(self.perfChart_plot, perfChart_frame) 
        self.perfChart_canvas.draw()
        self.perfChart_canvas._tkcanvas.grid(row=4,column=0,sticky='e')
        perfChart_tframe = tk.Frame(perfChart_frame)
        perfChart_tframe.grid(row=5,column=0)
        perfChart_toolbar = NavigationToolbar2Tk(self.perfChart_canvas,perfChart_tframe)

    def presetSelectResults(self,eventObject):

        selected = eventObject.widget.get()
        self.perfChart_subplot.cla()

        self.perfChart_subplot.set_title("GA performance chart")
        self.perfChart_subplot.set_ylabel("EPAM (%)")
        self.perfChart_subplot.set_xlabel('Generations')

        resultsData = pd.read_sql("SELECT * FROM resultsGA WHERE name ='%s'" % selected,gaCnx)
        resultsDataDrop = resultsData.drop_duplicates(subset='epam').reset_index() #this table has each individual's data multiplied by the number of genes, dropping to pick only one value

        alphas = [] #store the alpha individuals for each generation

        genNumber = len(resultsDataDrop['gen'].drop_duplicates().index) #pick the total of generations, an easy way
        
        for g in range(genNumber): #iterating over generations results

            alpha = resultsDataDrop.loc[resultsDataDrop['gen']==g]['epam'].sort_values().reset_index(drop=True)
            alphas.append(alpha[0]) #storing on a list

        x_data = range(genNumber)
        y_data = alphas

        self.perfChart_subplot.plot(x_data,y_data)
        self.perfChart_canvas.draw()

        #report Section

        self.reportFrame = tk.Frame(self.resultsGAWindow)
        self.reportFrame.grid(row=0,column=1)
        

        genesNumber = len(resultsData.drop_duplicates(subset='par_name').index)
        bestIndData = resultsData.sort_values(by='epam').reset_index(drop=True).iloc[:genesNumber]
        bestGen = bestIndData['gen'][0]
        bestInd = bestIndData['ind'][0]
        bestEPAM = bestIndData['epam'][0]

        self.bestGenLabel = tk.Label(self.reportFrame,text='Best generation: %s' % bestGen)
        self.bestGenLabel.grid(row=0,column=0,sticky='w')
        self.bestIndLabel = tk.Label(self.reportFrame,text='Best individual: %s\n' % bestInd)
        self.bestIndLabel.grid(row=1,column=0,sticky='w')
        self.bestEPAMLabel = tk.Label(self.reportFrame,text='Best EPAM: %s %%' % (round(bestEPAM*100,2)))
        self.bestEPAMLabel.grid(row=0,column=1,padx=10) 
        self.geneLabel = tk.Label(self.reportFrame,text='Genes: ')
        self.geneLabel.grid(row=2,column=0,sticky='w')
        self.geneFrame = tk.Frame(self.reportFrame)
        self.geneFrame.grid(row=3,column=0)

        for index, gene in bestIndData.iterrows():

            self.geneLabel = tk.Label(self.geneFrame,text='%s = %s' % (gene['par_name'],round(gene['par_value'],2)))
            self.geneLabel.pack(anchor=tk.W)

class runCalibration:

    #data initialization
    def __init__(self,name):

        #print(name)
        self.cfgGA = pd.read_sql(("select * from configurationsGA where name = '%s'" % name),gaCnx)
        self.parGA = pd.read_sql(("select * from parametersGA where name = '%s'" % name),gaCnx)
        self.resultsGA = pd.read_sql(("select * from resultsGA where name = '%s'" % name),gaCnx)

        self.gen0()
        self.genN()    
        self.name = name

    def simulationGA(self,name,gen,rep,ind,genes):


        datapoint_id = self.cfgGA['datapoint_id'].item()
        datapoint_name = self.cfgGA['datapoint_type'].item()
        perf_measure = self.cfgGA['perf_measure'].item()
        time_p =  'avg'
        field_value =  self.cfgGA['field_data'].item()
        
        
        for gene_name, gene_value in genes.items(): #sets parameters (called genes here)

            Vissim.Net.DrivingBehaviors[0].SetAttValue(gene_name, gene_value)
        
        Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
        Vissim.Simulation.RunContinuous() #Iniciando Simulação 

        seed = 40
        rep_results = []
        results = []
        
        for replication in range(1,rep+1):
            

            if datapoint_name == 'Data Collector':

                if perf_measure == 'Saturation Headway':
                    
                    #A função ja tem replication handling
                    result = calculate_shdwy(vissimFile, datapoint_id, replication) 
                    
                else:

                    selected_dc = Vissim.Net.DataCollectionMeasurements.ItemByKey(int(datapoint_id)) 
                    result = selected_dc.AttValue('{}({},{},All)'.format(str(perf_measure), 
                                                str(replication), 
                                                str('time_p')))

            elif datapoint_name == 'Travel Time Collector':

                selected_ttc = Vissim.Net.DelayMeasurements.ItemByKey(int(datapoint_id))
                result = selected_ttc.AttValue('{}({},{},All)'.format(str(perf_measure), 
                                            str(replication), 
                                            str(time_p)))
                                            
            else:    
                    
                    selected_qc = Vissim.Net.QueueCounters.ItemByKey(int(datapoint_id))
                    result = selected_qc.AttValue('{}({},{})'.format(str(perf_measure), 
                                                str(replication), 
                                                str(time_p)))

            seed = Vissim.Net.SimulationRuns.GetMultipleAttributes(['Randseed'])[0][0]

            fitness = abs((result-field_value)/result)

            rep_results.append(fitness)
            results.append(result)

        for p_name, p_value in genes.items():
            #print(ind)
            #print(seed)
            #print(gen)
            query = ("""INSERT INTO resultsGA (name,seed,gen,ind,par_name,par_value,perf_measure,result_value,epam) 
            VALUES ('%s',%s,%s,%s,'%s',%s,'%s',%s,%s)""" % (str(name),str(int(seed)),str(int(gen)),
                                                               str(int(ind)),str(p_name),str(p_value),
                                                               str(perf_measure),str(mean(results)),str(mean(rep_results))))
            #print(query)
            cursorGA.execute(query)
            gaCnx.commit()
        

    def gen0(self):

        name = 'teste'#TODO add name key from field in cfg window

        rep = self.cfgGA['rep'].item()
        ind = self.cfgGA['ind'].item()
        gen = 0

        Vissim.Simulation.SetAttValue('NumRuns', rep)
        
        for individual in range(ind): #generating gen0 individuals
            
            genes = {}

            for index, pdata in self.parGA.iterrows(): #creating gen0 ind genes
                
                up = pdata['parameter_b_value']
                down = pdata['parameter_u_value']
                gene_name = pdata['parameter_name']                
                gene_value = random.uniform(down,up)
                genes[gene_name] = gene_value

            print("\naqui esta a rep: %s\n" % rep)
            self.simulationGA(name,gen,rep,individual,genes)

    def genN(self):
        
        name = 'teste'
        cfgGA = pd.read_sql("SELECT * FROM configurationsGA WHERE name ='%s'" % name,gaCnx)
        parGA = pd.read_sql("SELECT * FROM parametersGA WHERE name ='%s'" % name,gaCnx)
        rep_number = cfgGA['rep'][0]
        ind_number = cfgGA['ind'][0]
        n_generations = int(cfgGA['gen'][0])
        #print(n_generations)

        #Vissim.Simulation.SetAttValue('NumRuns', rep_number)

        for gen in range(n_generations): #generations loop
            
            gen_number = gen
            #print('gen %s' % gen_number)
            old_genData = pd.read_sql(("SELECT * FROM resultsGA WHERE gen = %s AND name = '%s'" % (gen_number,name)),gaCnx)
            #print(old_genData)
            #print('\n')
            old_genData['rank'] = old_genData['epam'].rank(method='dense')
            old_genData = old_genData.sort_values(by='rank').reset_index()            
            cutRank = int(0.2*ind_number)+1    
            #print(old_genData)
            fitness = old_genData.loc[old_genData['rank']==1]['epam'][0]
            #print('gen: %s fitness = %s' % (gen_number,fitness))
            gen_number += 1
            #print(old_genData)
            #print('\n')
            #print('cut rank = %s' % cutRank)
            
            for ind in range(ind_number):
                
                old_genData_ind = old_genData.loc[old_genData['ind']==ind]
                
                #print(old_genData_ind)
                #print('\n')
                genes = {}
                
                for index_ind, old_ind in old_genData_ind.iterrows(): #individuals loop

                    rank = old_ind['rank']
                    gene_name = old_ind['par_name']
                    print(old_ind)
                    
                    if rank == 1: 

                        gene_value = old_ind['par_value']
                        genes[gene_name] = gene_value

                    elif rank > 1 and rank <= cutRank:  #parent gene heritage (crossover)   

                        gene_value = old_ind['par_value']*random.uniform(0.7,1.7)
                        genes[gene_name] = gene_value

                    else: #new random ind

                        up = parGA.loc[parGA['parameter_name']==gene_name]['parameter_u_value'].item() #gene upper limit
                        down = parGA.loc[parGA['parameter_name']==gene_name]['parameter_b_value'].item() #gene bottom limit
                        #print(down)
                        gene_value = np.random.uniform(int(down),int(up))
                        #print(gene_value)
                        genes[gene_name] = gene_value
                                    
                self.simulationGA(name,gen_number,rep_number,ind,genes)











app = SeaofBTCapp()
app.geometry("1920x1080")
app.state('zoomed')
app.mainloop()