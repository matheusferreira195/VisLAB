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

NORM_FONT= ("Roboto", 10)
LARGE_FONT = ("Roboto", 20)

#Database connection and set up

cnx = sqlite3.connect(r'C:\Users\mathe\Desktop\vislab.db')
cursor = cnx.cursor()

#Loading metadata dataframes 

dc_data = generate_dcdf_test()#generate_dcdf(Vissim)
parameter_db = pd.read_csv(r'E:\Google Drive\Scripts\vistools\resources\parameters.visdb')

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
        #print(existing_experiments[0])
        self.add_buttons = []        

        #getting the stickers from previous section (experiments saved on the db)

        for row in existing_experiments.iterrows():

                y = int(row[0])
                x = math.ceil((int(row[0])/4)+0.1)
                print(x)
                self.add_postit(x,y,exp=int(row[1]),btn_id=row[0])
        
        #dynamic search bar init

        self.search_var = tk.StringVar()        
        self.switch = False
        self.search_mem = ''
        

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

        button_edit = tk.Button(self, text = "Edit", command = lambda: self.edit_window(exp), anchor = tk.W)
        buttone_window = canvas.create_window(50, 150, anchor=tk.NW, window=button_edit)

        #TODO adicionar os outros 4 botoes

    def edit_window(self,experiment):
        #TODO Como eu colocaria mais de um parametro pro
        #print('experiment%i' % experiment)
        
        win = tk.Toplevel()
        win.wm_title("Window")

        l = tk.Label(win, text="Input")
        l.grid(row=0, column=0)
        
        b = tk.Button(win, text="Okay", command=lambda:  win.destroy)
        b.grid(row=7, column=0)

        m = tk.Button(win, text="Maria", command= lambda: messagebox.showinfo("Message", "Eu amo muito minha nemzudazoza :)"))
        m.grid(row=8, column=20)

        self.datapoints_label = tk.Label(win,text = 'Data Points')
        self.datapoints_ctype_dropdown = ttk.Combobox(win, width=25)
        self.datapoints_ctype_dropdown['values'] = list(dc_data['Display'])
        self.datapoints_ctype_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctype_dropdown.set('Select data collector type')
        self.datapoints_ctype_dropdown.bind('<<ComboboxSelected>>', lambda: self.datapoints_callback)

        self.separator = ttk.Separator(win, orient="vertical")

        self.datapoints_cperfmeasure_dropdown = ttk.Combobox(win, width=25)
        self.datapoints_cperfmeasure_dropdown['values'] = []
        self.datapoints_cperfmeasure_dropdown.configure(font=('Roboto', 8))
        self.datapoints_cperfmeasure_dropdown.set('Select what you will measure')
        self.datapoints_cperfmeasure_dropdown.bind('<<ComboboxSelected>>', lambda: self.datapoints_callback)

        self.datapoints_ctimeinterval_label = tk.Label(win, text='Add time interval number or agregation \n eg: 1,2,3,avg,min,max')
        self.datapoints_ctimeinterval_entry = tk.Entry(win)

        self.datapoints_ctargetvalue_label=tk.Label(win, text='Add the field data to compare')
        self.datapoints_ctargetvalue_entry= tk.Entry(win)

        self.datapoint_ok_button = tk.Button(win, command = lambda: self.button_callback)# image=self.check_image)

        ##------Parameters section------##   
        self.parameters_label = tk.Label(win,text = 'Parameters')      
        self.parameter_search_entry = tk.Entry(win, textvariable=self.search_var, width=25)
        self.parameter_search_entry.insert(0, 'Search parameters here')
        self.parameter_search_listbox = tk.Listbox(win, width=45, height=1)
        self.parameter_search_listbox.bind('<<ListboxSelect>>', lambda: self.parameters_callback)

        self.parameter_label_liminf = tk.Label(win, text = 'Inferior Limit')
        self.parameter_entry_liminf = tk.Entry(win, width=10)
        self.parameter_entry_liminf.bind('<FocusOut>', lambda: self.parameters_callback)

        self.parameter_label_limsup = tk.Label(win, text = 'Superior Limit')
        self.parameter_entry_limsup = tk.Entry(win, width=10)
        self.parameter_entry_limsup.bind('<FocusOut>',  lambda: self.parameters_callback)

        self.parameter_label_step = tk.Label(win, text = 'Step')
        self.parameter_entry_step = tk.Entry(win, width=10)
        self.parameter_entry_step.bind('<FocusOut>',  lambda: self.parameters_callback)

        ##------Simulation section------##
        self.simulation_label = tk.Label(win, text = 'Simulation Configs')

        self.simulation_label_replications = tk.Label(win, text = 'How many runs?')
        self.simulation_entry_replications = tk.Entry(win, width=5)

        self.test_button = tk.Button(win, command = lambda: self.test_buttom)#, image=self.check_image)

        ##------Grid configuration------##
        #self.experiment_label.grid(row=1, column=0, sticky='w')
        
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

        self.test_button.grid(row=7, column=5)
        
        #Function for updating the list/doing the search.
        #It needs to be called here to populate the listbox
        self.update_list()
        self.poll()
        
    
    def dummy(self):
        print('help')

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



#TODO adicionar closure das conexoes com a db para salvar os inserts e updates
app = SeaofBTCapp()
app.geometry("1280x720")    
app.mainloop()