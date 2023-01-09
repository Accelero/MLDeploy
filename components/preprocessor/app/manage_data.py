from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
from config import config
import csv
import pandas as pd
import numpy as np

class ManageData():
    def __init__(self):
        print('ManageData init')
        self.url = config.influxdb_url
        self.username = config.influxdb_username
        self.password = config.influxdb_password
        self.token = f'{self.username}:{self.password}'

        self.database_read = config.influxdb_database_read
        self.database_write = config.influxdb_database_write

        self.retention_policy = 'autogen'
        self.bucket = f'{self.database_read}/{self.retention_policy}'

        self.client = InfluxDBClient(url=self.url, token=self.token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

        # self.query = f'from(bucket: "{self.bucket}")\
        # |> range(start:-5)\
        # |> filter(fn: (r) => r._measurement == "FeaturesTraining")'
        # # \
        # # |> filter(fn: (r) => r["_field"] == "class_features0")'

        #self.create_database()
        self.query = f'from(bucket: "{self.bucket}")\
        |> range(start: -10)'
        #\
        #|> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")'
        # \
        # |> filter(fn: (r) => r._field == "Cur_X")'




    def create_database(self):
        print('ManageData create')

        print(f'create_Database {self.database_read} and {self.database_write}')
        request = requests.models.Response()
        #url_request = self.url+'/query'
        url_request = 'http://influxdb:8086/query'

        while request.status_code != 200:
            try:
                params = {'q':f'CREATE DATABASE {self.database_read}'}
                request = requests.post(url=url_request, params=params)
                params = {'q':f'CREATE DATABASE {self.database_write}'}
                request = requests.post(url=url_request, params=params)
            except:
                raise ValueError(f'Unexpectetd Value from InfluxDB {request.status_code}')

    def write_to_database(self, data):
        print('write to database')

        self.write_api.write(self.database_write,'wbk', record= data, data_frame_measurement_name = 'FeaturesInline')

        # self.write_api.write(self.bucket,'wbk', record={
        #     'measurement':'features',
        #     'fields':{'class_features':data['class_features'],
        #         'class_std':data['class_std'],
        #         'index_matrix':data['index_matrix'],
        #         'class_index_models':data['class_index_models']}})



    def read_from_database_input(self):
        df = self.query_api.query_data_frame(self.query)
        #df = self.query_api.query(query=self.query)

        df_strip=[]
        for i in df:
            df_strip.append(i.drop(columns=['result','_start','_stop','host','topic', '_measurement']))

        df_total = pd.DataFrame()
        #df_total['time'] = df[0]['_time']
        df_total['Pos_X'] = df[4]['_value']
        df_total['Pos_Y'] = df[5]['_value']
        df_total['Pos_Z'] = df[6]['_value']
        df_total['Speed_SP'] = df[7]['_value']
        df_total['Cur_X'] = df[1]['_value']
        df_total['Cur_Y'] = df[2]['_value']
        df_total['Cur_Z'] = df[3]['_value']
        df_total['Cur_SP'] = df[0]['_value']


        print(df_total)
        data =[]
        for l in range(len(df_total.index)):
            data.append(df_total.loc[l, :].values.flatten().tolist())

        head_data = ['Pos_X', 'Pos_Y', 'Pos_Z', 'Speed_SP', 'Cur_X', 'Cur_Y', 'Cur_Z', 'Cur_SP']

        print(len(data))
        data_arr = np.array(data)


        return head_data, data_arr

    def read_from_database_training(self):
        df = self.query_api.query_data_frame(f'from(bucket: "trainingData/autogen") |> range(start: -10)')
        print(df)
        #df = self.query_api.query(query=self.query)


# test as csv
    # def read_from_database(self):
    #     csv_result = self.query_api.query_csv(self.query)
    #     #df = self.query_api.query(query=self.query)
    #     #write to csv
    #     csv_file = open(r'./output.csv', "w",newline='')
    #     writer = csv.writer(csv_file)
    #     for row in csv_result:
    #         writer.writerow(row)
    #     csv_file.close()

    #     # print(df)
    #     # print(df[0])
    #     # print(type(df))
    #     # df_strip=[]
    #     # for i in df:
    #     #     df_strip.append(i.drop(columns=['result','_start','_stop','host','topic']))
    #     return True
