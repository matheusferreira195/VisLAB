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

#TODO encapsular codigo em funcao que dado um diretorio e um data collector, calcula o sheadway

def calculate_shdwy(path, dc, dc_number,sig_number):
    lsa_columns = ['SimSec', 'CycleSec', 'SC', 'SG', 'Aspect', 'Prev', 'Crit', 'duetoSG']
    os.chdir(path)
    mers = [file for file in glob.glob("*.mer")]
    lsas = [file for file in glob.glob("*.lsa")]

    for i in range(len(mers)):

        mer_data_raw = pd.read_csv(mers[i], sep=';', skiprows=(9+dc_number), skipinitialspace=True, index_col=False) 
        mer_data = mer_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

        lsa_data_raw = pd.read_csv(lsas[i], sep=';', skiprows=(9+sig_number), names=lsa_columns, skipinitialspace=True, index_col=False)
        lsa_data = lsa_data_raw.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

        green_windows = lsa_data[(lsa_data['Aspect'] == 'green') & (lsa_data['Aspect']=='red')]['SimSec']
        raw_green_windows = lsa_data.query('Aspect in list(["green", "red"])').reset_index(drop=True)


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

            
            df = cleaned_mer[(cleaned_mer['t(Entry)'] > green_windows[i][0]) 
                            & (cleaned_mer['t(Entry)'] < green_windows[i][1]) 
                            & (cleaned_mer['tQueue'] != 0)
                            & (cleaned_mer['Measurem.'] == dc)]
            
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
        

calculate_shdwy("E:\\Google Drive\Scripts\\vistools\\development\\net\\teste\\",1,5,2) #TODO pegar DC correto    