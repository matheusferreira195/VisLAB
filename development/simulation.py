def vissim_simulation(experiment,fake_data,fake_dc_data,fake_outputs):
        #This function sets up an runs the simulation for the selected experiment
        #runs = int(self.experiment_data.loc[self.experiment_data['Experiment']==experiment]['Runs'])
        runs = 2
        seed = 42
        #Vissim.Simulation.SetAttValue('RandSeed', seed)

        #Filtering parameter and data points meta data
        selected_parameters = fake_data.loc[fake_data.Experiment == experiment] #temporary test experiment cfg
        #selected_datapts = self.fake_dc_data.loc[self.fake_dc_data.Experiment == experiment] #temporary test experiment cfg

        #print(selected_parameters)

        raw_possibilities = {}

        for index, item in fake_data.iterrows(): #gets the parameter data for the selected experiment
            
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

        #------------------------------------#
                
        for index, parameters_df in parameters_df.iterrows():
            #print(parameters_df)

            parameter_names = list(parameters_df)

            #Configures the simulation
            for i in range(len(parameter_names)):

                parameter_name = str(parameter_names[i])
                parameter_df_ = int(parameters_df[i])

                Vissim.Net.DrivingBehaviors[0].SetAttValue(parameter_name,parameter_df_)
                #Vissim.Net.DrivingBehaviors[0].SetAttValue('W74ax',1)
                
            
            Vissim.Simulation.SetAttValue('RandSeed', seed)

            Vissim.Graphics.CurrentNetworkWindow.SetAttValue("QuickMode",1) #Ativando Quick Mode
            
            Vissim.Simulation.RunContinuous() #Iniciando Simulação 

            for index, dc_data in fake_dc_data.iterrows(): #Collects perf_measure data
                
                for replication in range(1,runs+1):
    
                    if dc_data['Data Point Type'] == 'Data Collector':
    
                        if dc_data['Perf_measure'] == 'Saturation Headway':
                            
                            #A função ja tem replication handling
                            headways = calculate_shdwy(path_network, dc_data['DP Number'].item) 
                            
                        else:
    
                            selected_dc = Vissim.Net.DataCollectionMeasurements.ItemByKey(int(dc_data['DP Number'])) 
                            result = selected_dc.AttValue('{}({},{},All)'.format(str(dc_data['Perf_measure']),str(replication), str(dc_data['Time Interval'])))
                     
                    elif dc_data['Data Point Type'] == 'Travel Time Collector':
                        
                        selected_ttc = Vissim.Net.DelayMeasurements.ItemByKey(int(dc_data['DP Number']))
                        result = selected_ttc.AttValue('{}({},{},All)'.format(str(dc_data['Perf_measure']),str(replication), str(dc_data['Time Interval'])))
                                                    
                    else:
    
                        
                        selected_qc = Vissim.Net.QueueCounters.ItemByKey(int(dc_data['DP Number']))
                        result = selected_qc.AttValue('{}({},{})'.format(str(dc_data['Perf_measure']), str(replication), str(dc_data['Time Interval'])))
                        
                    results = {'Experiment':1, 'Data Point Type':str(dc_data['Data Point Type']), 'DP Number':str(dc_data['DP Number']),'Perf_measure':str(dc_data['Perf_measure']),
                            'Time Interval':str(dc_data['Time Interval']),'Run':str(run),'Read data':str(result)}
    
                    results_data = results_data.append(results, ignore_index=True) #TODO Formatar para exportar pra dashboard

                results_data.to_csv(r"E:\Google Drive\Scripts\vistools\output.csv", sep = ';')