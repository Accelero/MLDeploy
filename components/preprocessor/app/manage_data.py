from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
from config import config

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
        |> range(start: -10)\
        |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")'
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



    def read_from_database(self):
        df = self.query_api.query_data_frame(self.query)
        #df = self.query_api.query(query=self.query)

        # print(df)
        # print(df[0])
        # print(type(df))
        df_strip=[]
        for i in df:
            df_strip.append(i.drop(columns=['result','_start','_stop','host','topic']))
        return df_strip
