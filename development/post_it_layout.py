
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

NORM_FONT= ("Roboto", 10)
LARGE_FONT = ("Roboto", 20)

#Database connection and set up

cnx = sqlite3.connect(r'C:\Users\mathe\Desktop\vislab.db')
cursor = cnx.cursor()

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

        for row in existing_experiments.iterrows():

                y = int(row[0])
                x = math.ceil(int(row[1])/4)
                print(x)
                self.add_postit(x,y,exp=int(row[1]),btn_id=row[0])

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
        

        #TODO adicionar os outros 4 botoes

    def add_postit(self,x,y,exp = 0, btn_id = None): #TODO associar o numero do database

        if btn_id != 0:
            self.add_buttons[btn_id-1].destroy()
        #Manages the post it backend
        if exp == 0:

            cursor.execute("INSERT INTO experiments DEFAULT VALUES")
            current_experiment = cursor.execute("SELECT * FROM experiments ORDER BY id DESC LIMIT 1").fetchone()[0]
            
        else:            

            current_experiment = exp

        canvas = tk.Canvas(self, relief = tk.FLAT, background = "#FFFF00",
                                            width = 300, height = 200)
        canvas.grid(row=x,column=y)
        
        #Navigation controls
        if y == 3:
            y = 0
            x += 1
        else:
            y += 1
            
        button_add = tk.Button(self, text = "Add", command = lambda: self.add_postit(x,y,btn_id=(current_experiment)), anchor = tk.W)
        self.add_buttons.append(button_add)        
        print("button %i"%(btn_id))
        button_window = canvas.create_window(10, 150, anchor=tk.NW, window=button_add)
        
        label_exp = tk.Label(self,text="Experiment %i" % (current_experiment),anchor=tk.CENTER)
        label_window = canvas.create_window(140,50,anchor=tk.CENTER,window=label_exp)

        button_edit = tk.Button(self, text = "Edit", command = lambda: self.edit_window(), anchor = tk.W)
        buttone_window = canvas.create_window(50, 150, anchor=tk.NW, window=button_edit)

    def edit_window(self):

        print('ok')
        win = tk.Toplevel()
        win.wm_title("Window")

        l = tk.Label(win, text="Input")
        l.grid(row=0, column=0)
        
        b = tk.Button(win, text="Okay", command=win.destroy)
        b.grid(row=7, column=0)

        m = tk.Button(win, text="Maria", command= lambda: messagebox.showinfo("Message", "Eu amo muito minha nemzudazoza :)"))
        m.grid(row=8, column=20)
        self.datapoints_label = tk.Label(win,text = 'Data Points')
        self.datapoints_ctype_dropdown = ttk.Combobox(win, width=25)
        self.datapoints_ctype_dropdown['values'] = [1,2,3,4]
        self.datapoints_ctype_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctype_dropdown.set('Select data collector type')
        self.datapoints_ctype_dropdown.bind('<<ComboboxSelected>>', self.dummy())

        self.separator = ttk.Separator(win, orient="vertical")

        self.datapoints_cperfmeasure_dropdown = ttk.Combobox(win, width=25)
        self.datapoints_cperfmeasure_dropdown['values'] = []
        self.datapoints_cperfmeasure_dropdown.configure(font=('Roboto', 8))
        self.datapoints_cperfmeasure_dropdown.set('Select what you will measure')
        self.datapoints_cperfmeasure_dropdown.bind('<<ComboboxSelected>>', self.dummy())

        self.datapoints_ctimeinterval_label = tk.Label(win, text='Add time interval number or agregation \n eg: 1,2,3,avg,min,max')
        self.datapoints_ctimeinterval_entry = tk.Entry(win)

        self.datapoints_ctargetvalue_label=tk.Label(win, text='Add the field data to compare')
        self.datapoints_ctargetvalue_entry= tk.Entry(win)

        self.datapoint_ok_button = tk.Button(win, command = lambda: self.dummy())# image=self.check_image)

        ##------Parameters section------##   
        self.parameters_label = tk.Label(win,text = 'Parameters')      
        self.parameter_search_entry = tk.Entry(win, textvariable=self.dummy(), width=25)
        self.parameter_search_entry.insert(0, 'Search parameters here')
        self.parameter_search_listbox = tk.Listbox(win, width=45, height=1)
        self.parameter_search_listbox.bind('<<ListboxSelect>>', self.dummy())

        self.parameter_label_liminf = tk.Label(win, text = 'Inferior Limit')
        self.parameter_entry_liminf = tk.Entry(win, width=10)
        self.parameter_entry_liminf.bind('<FocusOut>', self.dummy())

        self.parameter_label_limsup = tk.Label(win, text = 'Superior Limit')
        self.parameter_entry_limsup = tk.Entry(win, width=10)
        self.parameter_entry_limsup.bind('<FocusOut>', self.dummy())

        self.parameter_label_step = tk.Label(win, text = 'Step')
        self.parameter_entry_step = tk.Entry(win, width=10)
        self.parameter_entry_step.bind('<FocusOut>', self.dummy())

        ##------Simulation section------##
        self.simulation_label = tk.Label(win, text = 'Simulation Configs')

        self.simulation_label_replications = tk.Label(win, text = 'How many runs?')
        self.simulation_entry_replications = tk.Entry(win, width=5)

        self.test_button = tk.Button(win, command = lambda: self.dummy())#, image=self.check_image)

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



#TODO adicionar closure das conexoes com a db para salvar os inserts e updates
app = SeaofBTCapp()
app.geometry("1280x720")    
app.mainloop()