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
NORM_FONT= ("Roboto", 10)
LARGE_FONT = ("Roboto", 20)

#Database connection and set up

cnx = sqlite3.connect(r'E:\Google Drive\Scripts\vistools\resources\vislab.db')
cursor = cnx.cursor()

#Loading metadata dataframes 

#generate_dcdf(Vissim)

#main class

class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid(row=0,column=0)

        self.frames = {}

        for F in (StartPage, Board):

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

        button2 = tk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.grid(row=1,column=1)

dc_data = generate_dcdf_test()
parameter_db = pd.read_csv(r'E:\Google Drive\Scripts\vistools\resources\parameters.visdb')       
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
        print(self.datapoints_df)
        self.parameters_df = pd.read_sql(str('SELECT * FROM parameters'), cnx)
        self.results_df = pd.read_sql(str('SELECT * FROM results'), cnx)
        self.simulation_runs = pd.read_sql(str('SELECT * FROM simulation_runs'), cnx)
        self.results_df = pd.read_sql(str('SELECT * FROM results'), cnx)

        #print(existing_experiments[0])
        self.add_buttons = []        

        #getting the stickers from previous section (experiments saved on the db)

        for row in existing_experiments.iterrows():

                y = int(row[0])
                x = math.ceil((int(row[0])/4)+0.1)
                #print(x)
                self.add_postit(x,y,exp=int(row[1]),btn_id=row[0])
        
        #dynamic search bar init
        

        #Navigation

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0,column=1)

        button2 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.grid(row=0,column=2)
        
        button3 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button3.grid(row=0,column=2)
        


    def add_postit(self,x,y,exp = 0, btn_id = None): 
        
        #TODO change the add button to a standalone in the last position

        if btn_id != 0: #destroys the 'add' button for the first postit
            self.add_buttons[btn_id-1].destroy() 

        if exp == 0:

            cursor.execute("INSERT INTO experiments DEFAULT VALUES")
            current_experiment = cursor.execute("SELECT * FROM experiments ORDER BY id DESC LIMIT 1").fetchone()[0]
            
        else:            

            current_experiment = exp

        canvas = tk.Canvas(self, relief = tk.FLAT, background = "#FFFF00",
                                            width = 300, height = 200)
        canvas.grid(row=x,column=y)
        
        #defines the n+1 post it's position
        if y == 3:
            y = 0
            x += 1
        else:
            y += 1
            
        button_add = tk.Button(self, text = "Add", command = lambda: self.add_postit(x,y,btn_id=(current_experiment)), anchor = tk.W)
        self.add_buttons.append(button_add)        
        #print("button %i"%(btn_id))
        button_window = canvas.create_window(10, 150, anchor=tk.NW, window=button_add)
        
        label_exp = tk.Label(self,text="Experiment %i" % (current_experiment),anchor=tk.CENTER)
        label_window = canvas.create_window(140,50,anchor=tk.CENTER,window=label_exp)

        button_edit = tk.Button(self, text = "Edit", command = lambda: self.create_edit_windows(exp), anchor = tk.W)
        buttone_window = canvas.create_window(50, 150, anchor=tk.NW, window=button_edit)
        
    def create_edit_windows(self,exp):

        configurations = len(self.datapoints_df.loc[self.datapoints_df['experiment']==exp])
        if configurations == 0:
            configurations = 1

        win = tk.Toplevel()
        win.wm_title("Edit experiment")

        for i in range(configurations):

            edit_windows(experiment=exp,parent = win, cfg=(i+1))


        #TODO adicionar os outros 4 botoes

        
        #print(self.experiment_data)

    def client_exit(self):
        root.destroy()
        print("oi")

    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        self._geom=geom
        print(geom, self._geom)
        self.master.geometry(self._geom)

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
            
            raw_possibilities[parameter] = total_values #stores all the parameters values to be used laters


class edit_windows(tk.Frame):

    def __init__(self,parent,experiment,cfg):

        tk.Frame.__init__(self)

        self.datapoints_df = pd.read_sql(str('SELECT * FROM datapoints'), cnx)
        self.parameters_df = pd.read_sql(str('SELECT * FROM parameters'), cnx)   

        win = parent

        configurations = len(self.datapoints_df.loc[self.datapoints_df['experiment']==experiment])

        self.subframe = tk.Frame(win,height = 400, width = 400,highlightbackground="red", highlightcolor="red",highlightthickness=1,bd =0)
        self.subframe.grid(row=1+cfg,column=1)

        b = tk.Button(self.subframe, text="Okay", command=lambda:  win.destroy)

        self.search_var = tk.StringVar()
        self.switch = False
        self.search_mem = ''

        self.datapoints_label = tk.Label(self.subframe,text = 'Data Points')

        self.datapoints_ctype_dropdown = ttk.Combobox(self.subframe, width=25)
        self.datapoints_ctype_dropdown['values'] = list(dc_data['Display'])
        self.datapoints_ctype_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctype_dropdown.set('Select data collector type')
        self.datapoints_ctype_dropdown.bind('<<ComboboxSelected>>', lambda e: self.datapoints_callback(eventObject=e,experiment = experiment))

        self.separatorv = ttk.Separator(self.subframe, orient="vertical")

        self.datapoints_cperfmeasure_dropdown = ttk.Combobox(self.subframe, width=25)
        self.datapoints_cperfmeasure_dropdown['values'] = []
        self.datapoints_cperfmeasure_dropdown.configure(font=('Roboto', 8))
        self.datapoints_cperfmeasure_dropdown.set('Select what you will measure')
        self.datapoints_cperfmeasure_dropdown.bind('<<ComboboxSelected>>', lambda e: self.datapoints_callback(eventObject=e,experiment = experiment))

        self.datapoints_ctimeinterval_label = tk.Label(self.subframe, text='Add time interval number or agregation \n eg: 1,2,3,avg,min,max')

        self.datapoints_ctimeinterval_entry = tk.Entry(self.subframe)

        self.datapoints_ctargetvalue_label=tk.Label(self.subframe, text='Add the field data to compare')

        self.datapoints_ctargetvalue_entry= tk.Entry(self.subframe)

        self.datapoint_ok_button = tk.Button(self.subframe, text="Save Changes", command = lambda: self.save_exp_cfg(experiment))# image=self.check_image)
        
        ##------Parameters section------##
        self.parameters_label = tk.Label(self.subframe,text = 'Parameters')

        self.parameter_search_entry = tk.Entry(self.subframe, textvariable=self.search_var, width=25) 
        #FIXME tá sendo editada a mesma barra pra todos os campos
        self.parameter_search_entry.insert(0, 'Search parameters here')
        
        self.parameter_search_listbox = tk.Listbox(self.subframe, width=45, height=1)
        self.parameter_search_listbox.bind('<<ListboxSelect>>',  lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        self.parameter_label_liminf = tk.Label(self.subframe, text = 'Inferior Limit')
        self.parameter_entry_liminf = tk.Entry(self.subframe, width=10)
        self.parameter_entry_liminf.bind('<FocusOut>', lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        self.parameter_label_limsup = tk.Label(self.subframe, text = 'Superior Limit')
        self.parameter_entry_limsup = tk.Entry(self.subframe, width=10)
        self.parameter_entry_limsup.bind('<FocusOut>',lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        self.parameter_label_step = tk.Label(self.subframe, text = 'Step')

        self.parameter_entry_step = tk.Entry(self.subframe, width=10)
        self.parameter_entry_step.bind('<FocusOut>',lambda e: self.parameters_callback(eventObject=e,experiment = experiment))

        ##------Simulation section------##
        self.simulation_label = tk.Label(self.subframe, text = 'Simulation Configs')

        self.simulation_label_replications = tk.Label(self.subframe, text = 'How many runs?')

        self.simulation_entry_replications = tk.Entry(self.subframe, width=5)

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
    def save_exp_cfg(self,experiment): #save button

        print('pressde')

        ctarget_entry = self.datapoints_ctargetvalue_entry.get()
        ctimeinterval_entry = self.datapoints_ctimeinterval_entry.get()
        simruns_entry = self.simulation_entry_replications.get()
        print(ctarget_entry)
        self.datapoints_df.loc['field_value'] = ctarget_entry
        self.datapoints_df.loc['time_p'] = ctimeinterval_entry
        self.simulation_df.loc['replications'] = simruns_entry

        self.datapoints_df.to_sql('datapoints',cnx, if_exists='replace')
        self.simulation_df.to_sql('simulation_cfg',cnx,if_exists='replace')
        self.parameters_df.to_sql('parameters',cnx,if_exists='replace')

        print(self.parameters_df)
        print(self.datapoints_df)
        print(self.simulation_df)


    def parameters_callback(self,experiment, eventObject):
        #print(eventObject.widget)
        
        # you can also get the value off the eventObject
        caller = str(eventObject.widget)
        #experiment  = self.parameter_data.loc[self.parameter_data['Experiment']==self.experiment].index[0]
        #print(experiment)
        #print(self.parameter_data)

        if 'listbox' in caller:
            #print(self.parameter_search_listbox)
            selected = self.parameter_search_listbox.curselection()
            parameter_text = self.parameter_search_listbox.get(first=selected, last=None)

            parameter_identifier_row = parameter_db.loc[parameter_db['Long Name']==parameter_text]
            
            value = str(parameter_identifier_row['Identifier'].item())
            
            #print(value)          

            self.parameter_data.loc[experiment, 'Parameter'] = value
            #print(self.parameter_data.loc[experiment,])

            #print(self.parameter_data)

        else:

            value = eventObject.widget.get()        

        if 'entry4' in caller: #liminf          
            self.parameter_data.loc[experiment, 'Lim. Inf'] = value
            #print(self.parameter_data)
    
        elif 'entry5' in caller: #limsup  
            self.parameter_data.loc[experiment, 'Lim. Sup'] = value
            #print(self.parameter_data)

        elif 'entry6' in caller: #step
            self.parameter_data.loc[experiment, 'Step'] = value
        # print(self.parameter_data)
        
        else:
            experiment_index  = self.experiment_data.loc[self.experiment_data['Experiment']==self.experiment].index[0]
            dc_match = dc_data.loc[dc_data['Display'] == value]
            data_point_type = dc_match['Type'].item()
            Dc_Number = dc_match['No'].item()

            self.experiment_data.loc[experiment_index, 'Data Point Type'] = data_point_type
            self.experiment_data.loc[experiment_index, 'DP Number'] = Dc_Number
            #print(self.experiment_data)
        
        #print(self.experiment_data)
        
    def datapoints_callback(self, eventObject, experiment):
        # you can also get the value off the eventObject
        #TODO Logica pra saber qual linha do df é: carregar datapoints_df[datapoints_df['experiment']==]
        caller = str(eventObject.widget)
        value = eventObject.widget.get()
        print(caller)
        print(value)

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

#TODO adicionar closure das conexoes com a db para salvar os inserts e updates
app = SeaofBTCapp()
app.geometry("1280x720")    
app.mainloop()