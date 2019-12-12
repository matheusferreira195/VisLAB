import pandas as pd
import sqlite3
import numpy as np
import random
cnxGA = sqlite3.connect(r'E:\Google Drive\Scripts\VisLab\resources\ga.db')
cursorGA = cnxGA.cursor()

def simulationGA(name,gen,rep,ind,genes):

        '''Vissim = None #com.Dispatch('Vissim.Vissim')
        Vissim = com.Dispatch("Vissim.Vissim") #Abrindo o Vissim
        path_network =r'E:\Google Drive\Scripts\VisLab\development\net\teste\teste.inpx'
        flag = False 
        Vissim.LoadNet(path_network, flag) #Carregando o arquivo'''

        datapoint_id = cfgGA['datapoint_id']
        datapoint_name = cfgGA['datapoint_name']
        perf_measure = cfgGA['perf_measure'].item()
        time_p =  cfgGA['time_p']
        field_value =  cfgGA['field_data'].item()
        #Vissim.Simulation.SetAttValue('NumRuns', rep)
        
        for gene_name, gene_value in genes.items(): #sets parameters (called genes here)

            #print('%s = %s' % (gene_name,gene_value))
            pass

        seed = 40

        for replication in range(1,rep+1):
            seed += 1
            result = np.random.randn()
            fitness = abs((np.random.randn() - field_value) / field_value)
            
            for p_name,p_value in genes.items():
                
                
                query = ("""INSERT INTO resultsGA (name,seed,gen,ind,rep,par_name,par_value,perf_measure,result_value,epam) 
                VALUES ('%s',%s,%s,%s,%s,'%s',%s,'%s',%s,%s)""" % (str(name),str(seed),str(gen),
                                                                   str(ind),str(replication),str(p_name),str(p_value),
                                                                   str(perf_measure),str(result),str(fitness)))
                print(query)
                cursorGA.execute(query)
                cnxGA.commit()
def gen0():

        name = 'teste'#TODO add name key from field in cfg window

        rep = cfgGA['rep'].item()
        ind = cfgGA['ind'].item()
        gen = 0

        for individual in range(ind): #generating gen0 individuals
            
            genes = {}

            for index, pdata in parGA.iterrows(): #creating gen0 ind genes
                
                up = pdata['parameter_b_value']
                down = pdata['parameter_u_value']
                gene_name = pdata['parameter_name']                
                gene_value = random.uniform(down,up)
                genes[gene_name] = gene_value
            
            simulationGA(name,gen,rep,ind,genes)
def genN():
        
        name = 'teste'#TODO add name key from field in cfg window

        rep_number = cfgGA['rep'].item()
        ind_number = cfgGA['ind'].item()
        stopC_number = cfgGA['stop'].item()
        fitness = 1000000
        gen_number = 0

        while fitness > stopC_number: #generations loop
            
            old_genData = pd.read_sql(("""SELECT * FROM resultsGA WHERE gen = ?""",gen_number),cnxGA)
            old_genData = old_genData.sort_values(by='epam').reset_index()
            cutRank = int(0.2*ind_number)+1
            
            fitness = old_genData[0].item()

            print('gen = %s fitness = %s' % (gen_number,fitness))
            print(cutRank)

            gen_number += 1

            for index_ind, old_ind in genData.iterrows(): #individuals loop
                
                genes = {}

                for index_par, pdata in parGA.iterrows(): #creating new gen genes
                    
                    if old_ind['rank'] == 1:

                        gene_name = pdata['parameter_name'] #gene name
                        gene_value = old_ind['par_value']
                        genes[gene_name] = gene_value

                    elif old_ind['rank'] > 1 and old_ind['rank'] < cutRank:  #random gene mutation    

                        gene_name = pdata['parameter_name'] #gene name
                        gene_value = old_ind['par_value']*random.uniform(0.7,1.7)

                    else: #parent gene heritage (crossover)

                        up = pdata['parameter_u_value'] #gene upper limit
                        down = pdata['parameter_d_value'] #gene bottom limit
                        gene_value = random.uniform(down,up)
                        genes[gene_name] = gene_value

                    simulationGA(name,gen_number,rep_number,index_ind,genes)

name= 'teste'
cfgGA = pd.read_sql(("select * from configurationsGA where name = '%s'" % name),cnxGA)
parGA = pd.read_sql(("select * from parametersGA where name = '%s'" % name),cnxGA)
resultsGA = pd.read_sql(("select * from resultsGA where name = '%s'" % name),cnxGA)

gen0()
genN()