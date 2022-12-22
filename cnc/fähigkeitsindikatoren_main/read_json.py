import os
import pandas as pd
import json

# file to read json-files in an foulder and export data as csv-file
path = (r'C:\Users\stroebel\Documents\Daten_SDMflex\Versuch 1\SDMflex_V1_21')
machine = 'CMX'   # CMX, DMU
Data_file = []   # Initialize the data list
names = []   # Initialize the name List


foulder = os.listdir(path)

# read all json files in the selected foulder an add the Data to Data list
for file in foulder:
    if file.endswith('.json'):
        with open(path + '/' + file) as f:
                # Load data
            raw_data = json.load(f)

            # Get the names of the time series
            for i in raw_data['Header']['SignalListHFData']:
                names += [list(i.values())[3]]

            # Get the data of the time series
            for data in raw_data['Payload']:
                if 'HFData' in data.keys():
                    for row in data['HFData']:
                        Data_file += [row]

# Transpose data
Data = [[Data_file[s][i] for s in range(len(Data_file))] for i in range(len(Data_file[0]))]

# Get DataFrames for the selected machine
if machine == 'DMU':
    raw_data = {'Pos_X':Data[names.index('DES_POS|1')],'Pos_Y':Data[names.index('DES_POS|2')],'Pos_Z':Data[names.index('DES_POS|3')],'Pos_B':Data[names.index('DES_POS|4')],'Speed_SP':Data[names.index('CMD_SPEED|6')],
            'Cur_X':Data[names.index('CURRENT|1')],'Cur_Y':Data[names.index('CURRENT|2')],'Cur_Z':Data[names.index('CURRENT|3')],'Cur_B':Data[names.index('CURRENT|4')],'Cur_SP':Data[names.index('CURRENT|6')]}
if machine == 'CMX':
    raw_data = {'Pos_X':Data[names.index('DES_POS|1')],'Pos_Y':Data[names.index('DES_POS|2')],'Pos_Z':Data[names.index('DES_POS|3')],'Speed_SP':Data[names.index('CMD_SPEED|6')],
            'Cur_X':Data[names.index('CURRENT|1')],'Cur_Y':Data[names.index('CURRENT|2')],'Cur_Z':Data[names.index('CURRENT|3')],'Cur_SP':Data[names.index('CURRENT|6')]}

new_df=pd.DataFrame(data = raw_data)

# Save Data as CSV
new_df.to_csv(r'C:\\Users\stroebel\Documents\\Programme\\CSV_SDMflex\\' + path.split('\\')[-1] + '.csv', index=False)