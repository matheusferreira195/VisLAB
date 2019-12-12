# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 20:59:37 2019

@author: mathe
"""

import pandas as pd
import matplotlib
from simulation import vissim_simulation


fake_data_data = {'Experiment': [1,1,1,2,2], 
                  'Parameter': ['W74ax', 'W74bxAdd', 'W74bxMult','W74bxAdd', 'W74bxMult'], 
                  'Lim. Inf': [1,1,1,2,2], 
                  'Lim. Sup': [2,2,2,3,3], 
                  'Step': [1, 1, 1, 1, 1]}
fake_data = pd.DataFrame(fake_data_data, columns = ['Experiment', 'Parameter', 'Lim. Inf', 'Lim. Sup', 'Step'])

fake_dc_data_data = {'Experiment': [1,1,1], 'Data Point Type': ['Data Collector', 'Travel Time Collector', 'Queue Counter'],
                     'DP Number': [6,3,1], 
                     'Perf_measure': ['SpeedAvgArith','VehDelay','QLen'], 
                     'Time Interval': ['Avg','Avg','Avg'], 
                     'Field data': ['30','3.2','10']}
fake_dc_data = pd.DataFrame(fake_dc_data_data, columns = ['Experiment', 
                                                          'Data Point Type', 
                                                          'DP Number', 'Perf_measure', 
                                                          'Time Interval', 
                                                          'Field data']) 

fake_outputs = {'Data Point':
        }

simulation = vissim_simulation