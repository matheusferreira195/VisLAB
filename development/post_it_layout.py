
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 21:05:28 2019

@author: mathe
"""
import tkinter as tk

NORM_FONT= ("Roboto", 10)
LARGE_FONT = ("Roboto", 20)

class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.grid(row=0,column=0)

        self.frames = {}

        for F in (StartPage, PageOne):

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
        label.grid(row=0,column=1)

        button = tk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.grid(row=1,column=0)

        button2 = tk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.grid(row=1,column=1)
        
        #first sticker
        
        canvas1 = tk.Canvas(self, relief = tk.FLAT, background = "#FFFF00",
                                            width = 300, height = 200)
        canvas1.grid(row=2,column=1)

        
        button_add = tk.Button(self, text = "Add", command = lambda: self.add_postit(2,2), anchor = tk.W)
        button_add.configure(width = 10)
        buttonadd_window = canvas1.create_window(10, 10, anchor=tk.NW, window=button_add)
        
        label_exp = tk.Label(self,text="Experiment 1",anchor=tk.CENTER)
        label_window = canvas1.create_window(50,50,anchor=tk.CENTER,window=label_exp)
        
    
    def add_postit(self,x,y):
        
        canvas = tk.Canvas(self, relief = tk.FLAT, background = "#FFFF00",
                                            width = 300, height = 200,)
        canvas.grid(row=x,column=y)
        
        #Navigation controls
        if y == 4:
            y = 1
            x += 1
        else:
            y += 1
            
        button = tk.Button(self, text = "Add", command = lambda: self.add_postit(x,y), anchor = tk.W)
        button.configure(width = 10, activebackground = "#33B5E5", relief = tk.FLAT)
        button_window = canvas.create_window(10, 10, anchor=tk.NW, window=button)
        label_exp = tk.Label(self,text="Experiment 1",anchor=tk.CENTER)
        label_window = canvas.create_window(50,50,anchor=tk.CENTER,window=label_exp)
        
    
    
class PageOne(tk.Frame):

    #Experiment page, where the user models the sensitivity analysis experiments

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.grid(row=0,column=0)
        
        
        #canvas = tk.Canvas(width=800,height=400)
        #canvas.grid(row=2, column=2)
        #canvas.create_rectangle(10,10,160,160, fill = '#FFFF00')
        
        
        
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0,column=1)

        button2 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.grid(row=0,column=2)
        
        button3 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button3.grid(row=0,column=2)
        

app = SeaofBTCapp()
app.geometry("1600x768")    
app.mainloop()