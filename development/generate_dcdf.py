import pandas as pd
import win32com.client as com

def generate_dcdf(Vissim):

    dc_df = pd.DataFrame(columns = ['Type', 'Name', 'No', 'Display'])
    attribute=['Name', 'No']
    attributes_dcm=['Name', 'No', 'DataCollectionPoints']
    attributes_ttm=['Name', 'No', 'VehTravTmMeas']
    data_collectors_measurements_raw = Vissim.Net.DataCollectionMeasurements.GetMultipleAttributes(attributes_dcm)
    queue_counters_raw = Vissim.Net.QueueCounters.GetMultipleAttributes(attribute)
    travel_time_measurements_raw = Vissim.Net.DelayMeasurements.GetMultipleAttributes(attributes_ttm)

    print(data_collectors_measurements_raw)

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