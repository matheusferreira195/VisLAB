# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 16:21:06 2019

@author: mathe
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

mer = r'E:\Google Drive\Scripts\vistools\teste\teste_001.mer'
mer_data_raw = pd.read_csv(mer, sep=';', skiprows=10, skipinitialspace=True, index_col=False)
mer_data = mer_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

lsa = r'E:\Google Drive\Scripts\vistools\teste\teste_001.lsa'
lsa_columns = ['SimSec', 'CycleSec', 'SC', 'SG', 'Aspect', 'Prev', 'Crit', 'duetoSG']   

lsa_data_raw = pd.read_csv(lsa, sep=';', skiprows=10, names=lsa_columns, skipinitialspace=True, index_col=False)
lsa_data = lsa_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

green_windows = lsa_data[(lsa_data['Aspect'] == 'green') & (lsa_data['Aspect']=='red')]['SimSec']
raw_green_windows = lsa_data.query('Aspect in list(["green", "red"])').reset_index(drop=True)

#print(list(mer_data)[1])

cleaned_mer = mer_data[(mer_data['t(Entry)'] !=0 )]     
  
green_windows=[]
interval=[]
headways_df = pd.DataFrame(columns=['Cicle','Position','Headway'])
for i in range(len(raw_green_windows['SimSec']) -1):

    if raw_green_windows['Aspect'][i] == 'green':
              
        interval = [raw_green_windows['SimSec'][i],raw_green_windows['SimSec'][i+1]]    
        green_windows.append(interval)
        
for i in range(len(green_windows)):
    
    headways_to_bar = []

    
    df = cleaned_mer[(cleaned_mer['t(Entry)']>green_windows[i][0]) 
                    & (cleaned_mer['t(Entry)']<green_windows[i][1]) 
                    & (cleaned_mer['tQueue'] != 0)]
    
    if not df.empty:
        
        #print(df)
        
        filtrados = list(df['t(Entry)'])
        nao_filtrados = df['t(Entry)']
        print(filtrados)
        #print(nao_filtrados)
    
        for i in range(1,len(filtrados)):
            
            headway = filtrados[i] - filtrados[i-1]
            headways_dict = {'Cicle':green_windows[i],'Position':i, 'Headway': headway}
            headways_to_bar.append(headway)
            
            headways_df = headways_df.append(headways_dict, ignore_index = True)

        x = list(range(1,len(filtrados)))
        #print(x)
        y = headways_to_bar
        #print(y)
        plt.bar(x,y)
        plt.show()
print(headways_df)
        
    