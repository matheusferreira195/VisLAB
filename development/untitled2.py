import pandas as pd
import sqlite3
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D #<-- Note the capitalization! 
cnx = sqlite3.connect(r'E:\Google Drive\Scripts\vistools\resources\vislab.db')
data = pd.read_sql('SELECT * FROM simulation_runs WHERE experiment = 3',cnx)
x = data.loc[data['parameter_value']==1]['parameter_value']
y = data.loc[data['parameter_value']==3]['parameter_value']
z = data.loc[data['parameter_value']==1]['results']
fig = plt.figure()
ax1 = fig.add_subplot(111,projection='3d')
ax1.plot(x,y,z)