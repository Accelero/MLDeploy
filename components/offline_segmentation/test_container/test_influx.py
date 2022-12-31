#from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, WriteOptions
import csv
import requests
from config import config
import test_csv


client = InfluxDBClient(url='http://influxdb:8086', token='test:123')
#client.create_database('mydb2')
# list = client.get_list_database()
# print(list)

myQuery = f'from(bucket: "mydb")\
|> range(start: -10m)'
# \
# |> filter(fn: (r) => r._measurement == "sim_sensor")\
# |> filter(fn: (r) => r["_field"] == "value")'

def create_Database():
    print('create_Database')
    r = requests.models.Response()
    url = 'http://localhost:8086/query'


    while r.status_code != 200:
        try:
            params = {'q':'CREATE DATABASE mydb2'}
            r = requests.post(url=url, params=params)
        except:
            raise ValueError(f'Unexpectetd Value from InfluxDB {r.status_code}')



if __name__=='__main__':
    print('main preprozess')
    create_Database()

    test_csv.store_csv("C:/Users/jan-n_palfbg6/OneDrive - bwedu/000 Uni/7. Semester/BA/CNC/Code/MLDeploy/cnc/CSV_SDMflex/SDMflex_V2_Training_final.csv", url='http://localhost:8086/query')

    # query_api = client.query_api()
    # # get query as csv
    # csv_result = query_api.query_csv(query=myQuery)
    # #write to csv
    # csv_file = open(r'../cnc/output.csv', "w",newline='')
    # writer = csv.writer(csv_file)
    # for row in csv_result:
    #     writer.writerow(row)
    # csv_file.close()
