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

        self.database = config.influxdb_database
        self.retention_policy = 'autogen'
        self.bucket = f'{self.database}'#/{self.retention_policy}'

        self.client = InfluxDBClient(url=self.url, token=self.token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

        self.query = f'from(bucket: "{self.bucket}")\
        |> range(start: -1d)\
        |> filter(fn: (r) => r._measurement == "features")\
        |> filter(fn: (r) => r["_field"] == "feature")'

        self.create_database()



    def create_database(self):
        print('ManageData create')

        print(f'create_Database {self.database}')
        request = requests.models.Response()
        #url_request = self.url+'/query'
        url_request = 'http://influxdb:8086/query'

        while request.status_code != 200:
            try:
                params = {'q':f'CREATE DATABASE {self.database}'}
                request = requests.post(url=url_request, params=params)
            except:
                raise ValueError(f'Unexpectetd Value from InfluxDB {request.status_code}')

    def write_to_database(self, data):

        self.write_api.write(self.bucket,'wbk', record= data)

        # self.write_api.write(self.bucket,'wbk', record={
        #     'measurement':'features',
        #     'fields':{'class_features':data['class_features'],
        #         'class_std':data['class_std'],
        #         'index_matrix':data['index_matrix'],
        #         'class_index_models':data['class_index_models']}})



    def read_from_database(self):
        df = self.query_api.query_data_frame(self.query)
        print(df)
        df.to_csv('output_offline.csv', sep='\t', encoding='utf-8')
