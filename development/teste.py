import sqlite3
import pandas as pd
import sqlalchemy
cnx = sqlite3.connect(r'E:\Google Drive\Scripts\vistools\resources\vislab3.db')
cursor = cnx.cursor()

query_dp = str('SELECT * FROM datapoints WHERE experiment = #exp').replace('#exp',str(1))
query_pa = str('SELECT * FROM parameters WHERE experiment = #exp').replace('#exp',str(1))
query_sim = str('SELECT * FROM simulation_cfg WHERE experiment = #exp').replace('#exp',str(1))

datapoints_df = pd.read_sql(query_dp, cnx).iloc[1-1]
parameters_df = pd.read_sql(query_pa, cnx).iloc[1-1]
simulation_cfg = pd.read_sql(query_sim, cnx).iloc[1-1]

datapoints_df = datapoints_df.to_frame().T
print(datapoints_df)

datapoints_df.to_sql('datapoints',cnx,if_exists='replace', index = False)