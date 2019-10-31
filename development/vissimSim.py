import pandas as pd
import sqlite3
import itertools as it
import numpy as np

cnx = sqlite3.connect(r'C:\Users\Matheus Ferreira\Documents\Python Scripts\vislab.db')#, isolation_level=None)
cursor = cnx.cursor()

def vissim_simulation(experiment):

    simCfg = pd.read_sql(str('SELECT * FROM simulation_cfg WHERE experiment = %s' % experiment),cnx)
    selected_datapts = pd.read_sql(str('SELECT * FROM datapoints WHERE experiment = %s' % experiment),cnx) #self.datapoints_df.loc[self.datapoints_df['experiment']==experiment]
    selected_parameters = pd.read_sql(str('SELECT * FROM parameters WHERE experiment = %s' % experiment),cnx)#self.parameters_df.loc[self.parameters_df['experiment']==experiment]

    #print(selected_parameters)

    #This function sets up an runs the simulation for the selected experiment
    runs = int(simCfg['replications'])
    seed = int(simCfg['initial_seed'])
    seed_inc = int(simCfg['seed_increment'])

    #Vissim.Simulation.SetAttValue('RandSeed', seed)
    #Vissim.Simulation.SetAttValue('NumRuns', runs)

    raw_possibilities = {}

    for index, item in selected_parameters.iterrows(): #gets the parameter data for the selected experiment
        
        #print(item)
        
        parameter = item['parameter_name']
        inf = item['parameter_b_value']
        sup = item['parameter_u_value']
        step = item['parameter_step']
        
        if type(inf) == type(sup) == int or type(inf) == type(sup) == float: #verifies if the parameter is a int/float type or str/bool
            #print(type(inf))                                                #and processes accordingly
            total_values = np.arange(inf, sup+step, step)
            
        else:
            #print(inf)
            total_values = [inf, sup]
            
        #print(total_values)
        
        raw_possibilities[parameter] = total_values #stores all the parameters values to be used later

        
    allNames = sorted(raw_possibilities)
    combinations = list(it.product(*(raw_possibilities[Name] for Name in allNames))) #generates a list with all possible permutations
    #print(combinations)                                                             #of parameters
    #print(list(df.Parameter))
    
    selectedParameters = list(selected_parameters['parameter_name'])  #stores the parameter's names
    #print(selectedParameters)
    parameters_df = pd.DataFrame(combinations, columns=selectedParameters) #organizes all runs cfg data
    #print(parameters_df)
    #------------------------------------#
            
    for index, row in parameters_df.iterrows():
        #print(parameters_df)
        #print(row)
        parameter_names = list(parameters_df)
        #print(parameter_names)
        #print('parameter_names')
        #print(parameter_names)
        #Configures the simulation

        for i in range(len(parameter_names)):

            parameter_name = str(parameter_names[i])
            #print(parameter_name)
            parameter_df_ = int(row[i])
            #print(parameter_df_)
            #print(parameter_df_)        
            #print('%s = %s' % (parameter_name,str(parameter_df_)))

            for seed_m in range(1,runs+1):

                seed_t = seed+seed_m*seed_inc
                query = "INSERT INTO simulation_runs (experiment,parameter_name,parameter_value,seed) VALUES (%s,'%s',%s,%s)" % (str(experiment),
                                                                                                                         str(parameter_name),
                                                                                                                         str(parameter_df_),
                                                                                                                         str(seed_t))
                cursor.execute(query) 
            Vissim.Net.DrivingBehaviors[0].SetAttValue(parameter_name,parameter_df_)
            Vissim.Net.DrivingBehaviors[0].SetAttValue('W74ax',1)

        Vissim.Simulation.SetAttValue('RandSeed', seed)

        Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
        
        Vissim.Simulation.RunContinuous() #Iniciando Simulação 

        for index, dc_data in selected_datapts.iterrows(): #Collects perf_measure data #FIXME Trocar pra pegar os dc_data filtrados por experiemnto
            
            for replication in range(1,runs+1):
                
                if dc_data['dc_type'] == 'Data Collector':

                    if dc_data['perf_measure'] == 'Saturation Headway':
                        print('problema')
                        #A função ja tem replication handling
                        result = calculate_shdwy(path_network, dc_data['dc_number'].item, replication) 
                        
                    else:

                        selected_dc = Vissim.Net.DataCollectionMeasurements.ItemByKey(int(dc_data['dc_number'])) 
                        result = selected_dc.AttValue('{}({},{},All)'.format(str(dc_data['perf_measure']), 
                                                    str(replication), 
                                                    str(dc_data['time_p'])))

                elif dc_data['dc_type'] == 'Travel Time Collector':

                    selected_ttc = Vissim.Net.DelayMeasurements.ItemByKey(int(dc_data['dc_number']))
                    result = selected_ttc.AttValue('{}({},{},All)'.format(str(dc_data['perf_measure']), 
                                                str(replication), 
                                                str(dc_data['time_p'])))
                                                
                else:    
                    
                    selected_qc = Vissim.Net.QueueCounters.ItemByKey(int(dc_data['dc_number']))
                    result = selected_qc.AttValue('{}({},{})'.format(str(dc_data['perf_measure']), 
                                                str(replication), 
                                                str(dc_data['time_p'])))
                
                print(row)
                print('\n')

                for p_name,p_value in row.iteritems():

                    seedDb = seed + replication*seed_inc

                    cursor.execute("UPDATE simulation_runs SET results = %s WHERE experiment = %s AND parameter_name = %s AND parameter_value = %s AND seed = %s" % (result,experiment,p_name,p_value,seedDb))
        
        #self.results_data = self.results_data.append(results, ignore_index=True) #TODO Formatar para exportar pra dashboard

    #self.results_data.to_csv(r"E:\Google Drive\Scripts\vistools\output.csv", sep = ';')
    
vissim_simulation(experiment=3)