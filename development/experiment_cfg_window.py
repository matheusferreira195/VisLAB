#This is the second window that the user should see. It allows the user to configure a 'experiment',
#selecting first the net data collectors and its net perfomance measure (npm), and also 
#the driving behavior's parameters and the search range.



import tkinter as tk
from tkinter import ttk
from tkinter import *
import pandas as pd
NORM_FONT= ("Roboto", 10)


#test data
dc_data = pd.read_csv(r'E:\Google Drive\Scripts\vistools\resources\test.csv', sep=';')
dc_pm = ['velocity', 'flow']
dc_timeinterval = ['300-600', '600-900']

#function that models a popupmsg
def popupmsg(msg):
        popup = tk.Tk()
        popup.wm_title("!")
        label = ttk.Label(popup, text=msg, font=NORM_FONT)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
        B1.pack()
        popup.mainloop()

def datapoint_info(type):
    attribute=['Name', 'No']

    if type == 'data_collector':
        data_collectors = Vissim.Net.DataCollectionPoints.GetMultipleAttributes(attribute)
        return data_collectors
    if type == 'queue_counter':
        queue_counters = Vissim.Net.QueueCounters.GetMultipleAttributes(attribute)
        return queue_counters
    else:
        travel_times = Vissim.Net.VehicleTravelTimeMeasurements.GetMultipleAttributes(attribute)
        return travel_times


        
class Window(Frame): #similar a StartPage
        
    def __init__(self, master): #master = parent class (BTC_app no exemplo. É none por que nao há classes superiores 'essa é só uma janela' )
        print(type(master))
        Frame.__init__(self, master)
        
        container = tk.Frame(self)
        container.grid_rowconfigure(0, weight=1) 
        container.grid_columnconfigure(0, weight=1)
                
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
        self.datapoints_ctype_dropdown['values'] = ['Data Collector \n Pontes Vieira \n #1', 'Data Collector \n Santos Dummont \n #1'] #maybe I will use this format to condense the selection process
        self.datapoints_ctype_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctype_dropdown.set('Select data collector type')

        self.datapoints_cperfmeasure_dropdown = ttk.Combobox(self, width=25)
        self.datapoints_cperfmeasure_dropdown['values'] = ['Avg speed', 'Avg travel time', 'Max Queue Lenght', 'Avg flow speed']
        self.datapoints_cperfmeasure_dropdown.configure(font=('Roboto', 8))
        self.datapoints_cperfmeasure_dropdown.set('Select what you will measure')

        self.datapoints_ctimeinterval_dropdown = ttk.Combobox(self, width=25)
        self.datapoints_ctimeinterval_dropdown['values'] = ['300-600','600-900', '900-1200', 'All']
        self.datapoints_ctimeinterval_dropdown.configure(font=('Roboto', 8))
        self.datapoints_ctimeinterval_dropdown.set('Select what time interval we should consider')

        self.datapoints_ctargetvalue_label=Label(self, text='Add the field data to compare')
        self.datapoints_ctargetvalue_entry=Entry(self)

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