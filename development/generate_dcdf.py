import pandas as pd

def generate_dcdf_test():
    dc_df = pd.DataFrame(columns = ['Type', 'Name', 'No', 'Display'])

    for i in range(3):
        data = {'Type':'Data Collector', 'Name':'dc#%i' % i, 'No':'%i' % i, 'Data Collection Points':None, 'Display':('Data Collector' + '/ ' + 'N/A' + ' / #'+ str(i))}
        dc_df = dc_df.append(data,ignore_index=True)
    return dc_df
teste = generate_dcdf_test()
#print(teste)
teste_results = pd.read_csv(r'E:/Google Drive/Scripts/vistools/output.csv', sep=';')
experiment = 1
fake_data_data = {'Experiment': [1,1,1,2,2], 'Parameter': ['W74ax', 'W74bxAdd', 'W74bxMult','W74bxAdd', 'W74bxMult'], 'Lim. Inf': [1,1,1,2,2], 'Lim. Sup': [2,2,2,3,3], 'Step': [1, 1, 1, 1, 1]}
fake_data = pd.DataFrame(fake_data_data, columns = ['Experiment', 'Parameter', 'Lim. Inf', 'Lim. Sup', 'Step'])
fake_dc_data_data = {'Experiment': [1,1,1], 'Data Point Type': ['Data Collector', 'Travel Time Collector', 'Queue Counter'], 'DP Number': [6,3,1], 'Perf_measure': ['SpeedAvgArith','VehDelay','QLen'], 'Time Interval': ['Avg','Avg','Avg'], 'Field data': ['30','3.2','10']}
fake_dc_data = pd.DataFrame(fake_dc_data_data, columns = ['Experiment', 'Data Point Type', 'DP Number', 'Perf_measure', 'Time Interval', 'Field data'])
fake_selected_parameters = fake_data.loc[fake_data.Experiment == experiment] #temporary test experiment cfg


def generate_dcdf():

    dc_df = pd.DataFrame(columns = ['Type', 'Name', 'No', 'Display'])
    attribute=['Name', 'No']
    attributes_dcm=['Name', 'No', 'DataCollectionPoints']
    attributes_ttm=['Name', 'No', 'VehTravTmMeas']
    data_collectors_measurements_raw = Vissim.Net.DataCollectionMeasurements.GetMultipleAttributes(attributes_dcm)
    queue_counters_raw = Vissim.Net.QueueCounters.GetMultipleAttributes(attribute)
    travel_time_measurements_raw = Vissim.Net.DelayMeasurements.GetMultipleAttributes(attributes_ttm)

    for item in data_collectors_measurements_raw:

        if len(item[0]) == 0:
            data = {'Type':'Data Collector', 'Name':'Empty', 'No':item[1], 'Data Collection Points':item[2], 'Display':('Data Collector' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Data Collector', 'Name':item[0], 'No':item[1], 'Data Collection Points':item[2], 'Display':('Data Collector' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)

    for item in queue_counters_raw:
        if len(item[0]) == 0:
            data = {'Type':'Queue Counter', 'Name':'Empty', 'No':item[1], 'Display':('Queue Counter' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Queue Counter', 'Name':item[0], 'No':item[1], 'Display':('Queue Counter' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)

    for item in travel_time_measurements_raw:
        if len(item[0]) == 0:
            data = {'Type':'Travel Time Collector', 'Name':'Empty', 'No':item[1], 'Time Travel Points':item[2], 'Display':('Travel Time Collector' + '/ ' + 'N/A' + ' / #'+ str(item[1]))}
        else:
            data = {'Type':'Travel Time Collector', 'Name':item[0], 'No':item[1],'Time Travel Points':item[2], 'Display':('Travel Time Collector' + '/ ' + str(item[0]) + ' / #'+ str(item[1]))}
        dc_df = dc_df.append(data, ignore_index = True)
    #print(dc_df)
    return dc_df