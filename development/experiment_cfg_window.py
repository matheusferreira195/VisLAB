#This is the second window that the user should see. It allows the user to configure a 'experiment',
#selecting first the net data collectors and its net perfomance measure (npm), and also 
#the driving behavior's parameters and the search range.


import win32com.client as com
import tkinter as tk
from tkinter import ttk
from tkinter import *
import pandas as pd
import os

NORM_FONT= ("Roboto", 10)

#-------------------------------------------------------------------
Vissim = com.Dispatch("Vissim.Vissim") #Abrindo o Vissim
path_network = r'C:\Users\Matheus Ferreira\Google Drive\Scripts\vistools\development\net\teste.inpx'
flag = False 
Vissim.LoadNet(path_network, flag) #Carregando o arquivo
#ctypes.windll.user32.MessageBoxW(0, "Net loaded", "Vissim ready", 1)
print('net loaded\n')

#--------------------------------------------------------------------
#test data

dc_data = pd.DataFrame(columns = ['Type', 'Name', 'No', 'Perf_measure', 'Time interval', 'Field data', 'Display'])




#---------------------------------------------------------------------
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

    data_collectors_raw = Vissim.Net.DataCollectionPoints.GetMultipleAttributes(attribute)
    queue_counters_raw = Vissim.Net.QueueCounters.GetMultipleAttributes(attribute)
    travel_times_raw = Vissim.Net.VehicleTravelTimeMeasurements.GetMultipleAttributes(attribute)
    
    for item in data_collectors_raw:
        if len(item[0]) == 0:
            data = {'Type':'Data Collector', 'Name':'Empty', 'No':item[1], 'Display':('Data Collector' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Data Collector', 'Name':item[0], 'No':item[1], 'Display':('Data Collector' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)

    for item in queue_counters_raw:
        if len(item[0]) == 0:
            data = {'Type':'Queue Counter', 'Name':'Empty', 'No':item[1], 'Display':('Queue Counter' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Queue Counter', 'Name':item[0], 'No':item[1], 'Display':('Queue Counter' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)

    for item in travel_times_raw:
        if len(item[0]) == 0:
            data = {'Type':'Travel Time Collector', 'Name':'Empty', 'No':item[1], 'Display':('Travel Time Collector' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Travel Time Collector', 'Name':item[0], 'No':item[1], 'Display':('Travel Time Collector' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
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

        self.experiment_data = pd.DataFrame({'Experiment', 'Data Point Type', 'DP Number', 'Perf_measure', 'Time interval', 'Field data'})
        
        self.master = master
        
        self.search_var = StringVar()
        
        self.switch = False
        self.search_mem = ''
        self.experiment = 1
        
        self.collector_type = StringVar()
        self.collector_name = StringVar()
        self.collector_no = StringVar()
        self.collector_pm = StringVar()
        self.collector_timeinterval = StringVar()
        
        self.grid(row=0, column=0)

        self.init_window()
        
       
    def init_window(self):        
        
        self.master.title("GUI")
        
        #quitButton = Button(self, text = "Quit", command=self.client_exit)
        
        #quitButton.place(x=245, y=170)
        
        menu = Menu(self.master)
        self.master.config(menu=menu)
        
        file = Menu(menu)
        
        file.add_command(label = 'Exit', command = self.client_exit)
        
        menu.add_cascade(label="File", menu=file)
        
        edit = Menu(menu)     
                
        edit.add_command(label = 'Undo', command = lambda:popupmsg("wow! such programmin'"))
        
        menu.add_cascade(label='Edit', menu=edit)

        #Experiment fields
        self.experiment_text = str('Experiment %i' % self.experiment)
        self.experiment_label = Label(self,text = self.experiment_text)
        
        #Datapoint fields
        self.datapoints_label = Label(self,text = 'Data Points')
        self.datapoints_ctype_dropdown = ttk.Combobox(self, width=25)
        self.datapoints_ctype_dropdown['values'] = list(self.dc_data['Display'])
        self.datapoints_ctype_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctype_dropdown.set('Select data collector type')
        self.datapoints_ctype_dropdown.bind('<<ComboboxSelected>>', self.datapoints_callback('ctype'))

        self.datapoints_cperfmeasure_dropdown = ttk.Combobox(self, width=25)
        self.datapoints_cperfmeasure_dropdown['values'] = ['Avg speed', 'Avg travel time', 'Max Queue Lenght', 'Avg flow speed']
        self.datapoints_cperfmeasure_dropdown.configure(font=('Roboto', 8))
        self.datapoints_cperfmeasure_dropdown.set('Select what you will measure')
        self.datapoints_cperfmeasure_dropdown.bind('<<ComboboxSelected>>', self.datapoints_callback('cperfmeasure'))

        self.datapoints_ctimeinterval_dropdown = ttk.Combobox(self, width=25)
        self.datapoints_ctimeinterval_dropdown['values'] = ['300-600','600-900', '900-1200', 'All']
        self.datapoints_ctimeinterval_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctimeinterval_dropdown.set('Select what time interval we should consider')
        self.datapoints_ctimeinterval_dropdown.bind('<<ComboboxSelected>>', self.datapoints_callback('ctimeinterval'))

        self.datapoints_ctargetvalue_label=Label(self, text='Add the field data to compare')
        self.datapoints_ctargetvalue_entry=Entry(self)

        self.datapoint_ok_button = Button(self, image = )
        #self.experiment_data['Target'] = self.datapoints_ctargetvalue_entry.get()

        #separator

        #self.separator_dataxparameters = ttk.Separator()

        #Parameters field     
        self.parameters_label = Label(self,text = 'Parameters')      
        self.parameter_search_entry = Entry(self, textvariable=self.search_var, width=25)
        self.parameter_search_entry.insert(0, 'Search parameters here')
        self.parameter_search_listbox = Listbox(self, width=45, height=1)
                
        #self.OptionMenu(master, self.collector_type)
        
        #Grid configuration
        self.experiment_label.grid(row=1, column=0, sticky=W)
        
        
        self.datapoints_label.grid(row=2, column=0, sticky=W, padx=10)
        self.datapoints_ctype_dropdown.grid(row=4, column=0, sticky=W, padx=10)
        self.datapoints_cperfmeasure_dropdown.grid(row=4, column=1, sticky=W, padx=10)
        self.datapoints_ctimeinterval_dropdown.grid(row=4, column=2, sticky=W, padx=10)
        self.datapoints_ctargetvalue_label.grid(row=3, column=3, sticky=W, padx=10)
        self.datapoints_ctargetvalue_entry.grid(row=4, column=3, sticky=W, padx=10)

        self.parameters_label.grid(row=2, column=5, sticky=W, padx = 50)
        self.parameter_search_entry.grid(row=3, column=5, sticky =W, padx = 50)
        self.parameter_search_listbox.grid(row=4, column=5, sticky=W, padx = 50)
        
        
        
        #Function for updating the list/doing the search.
        #It needs to be called here to populate the listbox.
        self.update_list()

        self.poll()

    def datapoints_callback(self, eventObject, type):
        # you can also get the value off the eventObject
        dc_selected = eventObject.widget.get()

        if type == 'ctype':
            dc_correspondent = self.dc_data.loc[self.dc_data['Display'] == dc_selected]
            #print(dc_correpondent)
            
            experiment_entry = pd.Series(data={'Experiment':self.experiment, 'Data Point Type':dc_correspondent['Type'], 'DP Number':dc_correpondent['No']}, index=['Experiment', 'Data Point Type', 'Dp Number'])
            self.experiment_data = self.experiment_data.append(experiment_entry, ignore_index = True)

        if type == 'cperfmeasure':
            experiment_data.at[self.experiment, 'Perf_measure'] = dc_selected
        
        if type == 'ctimeinterval':
            experiment_data.at[self.experiment, 'Time Interval'] = dc_selected

        if type == 'target':
            experiment_data.at[self.experiment, 'Field Data'] = dc_selected

        print(experiment_entry)

    def client_exit(self):
        root.destroy()
        print("oi")

    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom    
    
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
        lbox_list = ['Adam', 'Lucy', 'Barry', 'Bob', 'James', 'Frank', 'Susan', 'Amanda', 'Christie']

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
    
        
root = Tk()
root.geometry("1920x1080")
root.state('zoomed')
app = Window(master = root)
root.mainloop()