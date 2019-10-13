# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 20:29:47 2019

@author: mathe
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import itertools as it


data = pd.read_csv(r'E:/Google Drive/Scripts/vistools/output.csv', sep=';')

experiment = 1
fake_data_data = {'Experiment': [1,1,1,2,2], 'Parameter': ['W74ax', 'W74bxAdd', 'W74bxMult','W74bxAdd', 'W74bxMult'], 'Lim. Inf': [1,1,1,2,2], 'Lim. Sup': [2,2,2,3,3], 'Step': [1, 1, 1, 1, 1]}
fake_data = pd.DataFrame(fake_data_data, columns = ['Experiment', 'Parameter', 'Lim. Inf', 'Lim. Sup', 'Step'])
fake_dc_data_data = {'Experiment': [1,1,1], 'Data Point Type': ['Data Collector', 'Travel Time Collector', 'Queue Counter'], 'DP Number': [6,3,1], 'Perf_measure': ['SpeedAvgArith','VehDelay','QLen'], 'Time Interval': ['Avg','Avg','Avg'], 'Field data': ['30','3.2','10']}
fake_dc_data = pd.DataFrame(fake_dc_data_data, columns = ['Experiment', 'Data Point Type', 'DP Number', 'Perf_measure', 'Time Interval', 'Field data'])
selected_parameters = fake_data.loc[fake_data.Experiment == experiment] #temporary test experiment cfg

raw_possibilities = {}

for index, item in selected_parameters.iterrows(): #FIXME 
    #gets the parameter data for the selected experiment
    
   #print(item)
    
    parameter = item['Parameter']
    inf = item['Lim. Inf']
    sup = item['Lim. Sup']
    step = item['Step']
    
    if type(inf) == type(sup) == int or type(inf) == type(sup) == float: #verifies if the parameter is a int/float type or str/bool
        #print(type(inf))                                                #and processes accordingly
        total_values = np.arange(inf, sup+step, step)
        
    else:
        #print(inf)
        total_values = [inf, sup]
        
    #print(total_values)
    
    raw_possibilities[parameter] = total_values #stores all the parameters values to be used later

#print(raw_possibilities)
allNames = sorted(raw_possibilities)
combinations = list(it.product(*(raw_possibilities[Name] for Name in allNames))) #generates a list with all possible permutations
#print(combinations)                                                             #of parameters
#print(list(df.Parameter))

selected_parameters = list(selected_parameters.Parameter)  #stores the parameter's names
parameters_df = pd.DataFrame(combinations, columns=selected_parameters) #organizes all runs cfg data
#print(parameters_df)
for index, parameter_data in parameters_df.iterrows():
    #print(parameter_data)
    
    parameter_names = list(parameters_df)
    
    #Configures the simulation
    for i in range(len(parameter_names)):
    
        parameter_name = str(parameter_names[i])
        parameter_data_ = int(parameter_data[i])
        #print(parameter_data_)
        #Vissim.Net.DrivingBehaviors[0].SetAttValue(parameter_name,parameter_data_)
        #Vissim.Net.DrivingBehaviors[0].SetAttValue('W74ax',1) 



###########################################################################################################################

#plot
def plots_single(parameter, perf_measure, p_type, title, experiment):
    
    #getting the parameters and results data by selected experiment
    #parameters_df_by_experiment = parameters_df.loc[parameters_df['Experiment']==experiment]
    data_by_experiment = data.loc[data['Experiment']==experiment]
    
    #getting the data of the max/min parameter value
    parameter_min = parameters_df[parameter].idxmin()
    parameter_max = parameters_df[parameter].idxmax()
    
    #if the graph is a scatterplot
    if p_type == 0:        
    
        results_min = list(data_by_experiment.loc[(data_by_experiment['Parameters']==parameter_min) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data'])
        results_max = list(data_by_experiment.loc[(data_by_experiment['Parameters']==parameter_max) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data'])
        
        print(results_min)
        print(results_max)
        
        plt.scatter(results_min, results_max, color='g')
        plt.xlabel(perf_measure + ' Min.')
        plt.ylabel(perf_measure + ' Máx.')
        plt.title(parameter)
        plt.show()
    
    #if the graph is a line chart, by runs
    if p_type == 1:
        
        results_min = np.asarray(list(data_by_experiment.loc[(data['Parameters']==parameter_min) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data']))
        results_max = np.asarray(list(data_by_experiment.loc[(data['Parameters']==parameter_max) & (data_by_experiment['Perf_measure']==perf_measure)]['Read data']))
        
        print(results_min)
        print(results_max)
        
        rep = np.asarray(list(set(list(data_by_experiment['Run'].loc[data_by_experiment['Parameters']==parameter_min]))))
        
        print(rep)
        #results_min = [1,2]
        #results_max = [3,4]
        #rep = [9,8]
        plt.plot(rep, results_min, color='green')
        plt.plot(rep, results_max, color='blue')
        plt.xlabel(perf_measure)
        plt.ylabel('# Simulations')
        plt.xticks(rep)
        plt.title(parameter)
        plt.show()

print(plots_single('W74ax','SpeedAvgArith',1,None,1))
            
        

            
           