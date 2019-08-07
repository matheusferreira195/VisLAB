#That file converts a .csv file with the short and long name of the Vissim parameters, of all of the models, with it default values, to a
#mysql database.

import mysql.connector
import pandas as pd
from tkinter import *

mydb = mysql.connector.connect (

  host = "localhost",
  user = "test_python_PG", #development
  passwd = "34064031",
  database = "test_PG" #development

)

mycursor = mydb.cursor()

#Code chunck to add columns

#mycursor.execute("ALTER TABLE drivingb ADD default_value VARCHAR(255)") 

#mycursor.execute("SHOW TABLES")

#for table in mycursor:
 # print(table)

#mycursor.execute("CREATE TABLE drivingb (name VARCHAR(255), shortname VARCHAR(255))")


#loading the files with the parameters data
df = pd.read_csv("E:\Google Drive\Scripts\AG_PG\parametros.csv", sep=";")

file_in = open("E:\Google Drive\Scripts\AG_PG\dados.txt", "r")
file_out = open("file_out.txt", "w")
lines = file_in.readlines()

defaults = []

for i in range(len(lines)):

  if lines[i] == "Default value\n":

    default = lines[i+2].replace('\n', '')
    file_out.write(default)
    defaults.append(default)    
    
df['Default'] = defaults

#sqlformula to add all of the parameters data into the database

sqlFormula = "INSERT INTO drivingb (name, shortname, default_value) VALUES (%s, %s, %s)"

for index, row in df.iterrows():
  parameter = (row["Long Name"], row["Short Name"], row["Default"]) 
  mycursor.execute(sqlFormula, parameter)
  mydb.commit()
