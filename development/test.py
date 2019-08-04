#!/usr/bin/python
#-*- coding: utf-8 -*-

import tkinter
from tkinter import *
import MySQLdb

#----------------------------------------------------------------------

class MainWindow():

    def __init__(self, root):
        frame = Frame(root, width=500, height=500)
        #root.minsize(300,300)
        frame.pack()


        # here we make  text input field

        self.E1 = Entry(frame, bd=2)
        self.E1.pack(side=TOP)

        # here the list generated from entry but covering it completely is bad ?? 

        self.Lb1 = Listbox(frame, bd=2)
        #Lb1.pack(side=BOTTOM)

        root.bind("<Key>", self.clickme)

        # open database (only once) at start program
        self.db = MySQLdb.connect("127.0.0.1", "root", "34064031", "test", use_unicode=True, charset="utf8")

    #-------------------

    def __del__(self): 
        # close database on exit
        self.db.close()

    #-------------------

    def clickme(self, x):

        txt = self.E1.get()

        self.Lb1.delete(0, END) # delete all on list

        if txt == '':
            self.Lb1.pack_forget() # hide list
        else:
            self.Lb1.pack(side=BOTTOM) # show list

            txt_for_query = txt + "%"  

            cursor = self.db.cursor()

            cursor.execute("SELECT name FROM `table` WHERE name LIKE '%s'" % (txt_for_query))

            res = cursor.fetchall() 

            for line in res: 
                self.Lb1.insert(END, line[0].encode('utf-8')) # append list

            cursor.close()

#----------------------------------------------------------------------

root = Tk()
MainWindow(root)
root.mainloop()