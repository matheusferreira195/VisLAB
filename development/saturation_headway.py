# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 16:21:06 2019

@author: mathe
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import glob
import os

def formatting(tipe, path):
    skipline = 0
    
    if tipe == '.mer':
        keyword = ' Measurem.'
        
    elif tipe == '.lsa':
        keyword = 'SC'
    
    with open(path) as f:
        
        lines = f.readlines()
        
        for chunk in enumerate(lines):
            if keyword in chunk[1]:
                
                if tipe == '.lsa':
                
                    skipline = int(chunk[0] + 2)
                    
                else:
                    skipline = int(chunk[0])
        #print(skipline)    
        return skipline
    

def calculate_shdwy(path, dc):
    lsa_columns = ['SimSec', 'CycleSec', 'SC', 'SG', 'Aspect', 'Prev', 'Crit', 'duetoSG']
    os.chdir(path)
    mers = [file for file in glob.glob("*.mer")]
    lsas = [file for file in glob.glob("*.lsa")]
    headways_df = pd.DataFrame(columns=['Replication','Cicle','Position','Headway'])
    #print(mers)
    #print(len(mers))
    for i in range(len(mers)):

        print(mers[i])

        mer_data_raw = pd.read_csv(mers[i], sep=';', skiprows=formatting('.mer',mers[i]), skipinitialspace=True, index_col=False) 
        mer_data = mer_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        #print(mer_data_raw)
        lsa_data_raw = pd.read_csv(lsas[i], sep=';', skiprows=formatting('.lsa',lsas[i]), names=lsa_columns, skipinitialspace=True, index_col=False)
        lsa_data = lsa_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        #print(lsa_data_raw)
        green_windows = lsa_data[(lsa_data['Aspect'] == 'green') & (lsa_data['Aspect']=='red')]['SimSec']
        raw_green_windows = lsa_data.query('Aspect in list(["green", "red"])').reset_index(drop=True)

        cleaned_mer = mer_data[(mer_data['t(Entry)'] !=0 )]     
        
        green_windows=[]
        interval=[]
        
        for w in range(len(raw_green_windows['SimSec']) -1):

            if raw_green_windows['Aspect'][w] == 'green':
                    
                interval = [raw_green_windows['SimSec'][w],raw_green_windows['SimSec'][w+1]]    
                green_windows.append(interval)
         
        for j in range(len(green_windows)):
            
            headways_to_bar = []

            
            df = cleaned_mer[(cleaned_mer['t(Entry)'] > green_windows[j][0]) 
                            & (cleaned_mer['t(Entry)'] < green_windows[j][1]) 
                            & (cleaned_mer['tQueue'] != 0)
                            & (cleaned_mer['Measurem.'] == dc)]
            
            if not df.empty:
                
                
                filtrados = list(df['t(Entry)'])

                if len(filtrados) >= 4:

                    for k in range(1,len(filtrados)):
                        
                        headway = filtrados[k] - filtrados[k-1]
                        headways_dict = {'Replication':i,'Cicle':green_windows[j],'Position':k, 'Headway': headway}
                        headways_to_bar.append(headway)
                        
                        headways_df = headways_df.append(headways_dict, ignore_index = True)
                
    return headways_df 
        

#h = calculate_shdwy("E:\\Google Drive\\Scripts\\vistools\\development\\net\\teste\\",5) 
#print(h) 