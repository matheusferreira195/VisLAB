import pandas as pd
from tkinter import *


df = pd.read_csv(r"E:\Google Drive\Scripts\vistools\resources\parameters.visdb", sep=",")
print(df)
'''
#First create application class
class DynamicSearch(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        #These variables will be used in the poll function so i 
        #Set them at the start of the program to avoid errors.
        self.search_var = StringVar()
        self.switch = False
        self.search_mem = ''

        self.pack()
        self.create_widgets()

    #Create main GUI window
    def create_widgets(self):
        #Use the StringVar we set up in the __init__ function 
        #as the variable for the entry box
        self.entry = Entry(self, textvariable=self.search_var, width=13)
        self.lbox = Listbox(self, width=45, height=15)

        self.entry.grid(row=0, column=0, padx=10, pady=3)
        self.lbox.grid(row=1, column=0, padx=10, pady=3)
        
        #Function for updating the list/doing the search.
        #It needs to be called here to populate the listbox.
        self.update_list()

        self.poll()

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

        self.lbox.delete(0, END)

        for item in df["Long Name"]:
            if is_contact_search == True:
                #Searches contents of lbox_list and only inserts
                #the item to the list if it self.search is in 
                #the current item.
                if self.search.lower() in item.lower():
                    self.lbox.insert(END, item)
            else:
                self.lbox.insert(END, item)

root = Tk()
root.title('Filter Listbox Test')
app = DynamicSearch(master=root)
print ('Starting mainloop()')
app.mainloop()
'''