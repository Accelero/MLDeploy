# from influxdb_client import InfluxDBClient, WriteOptions
# from influxdb_client.client.write_api import SYNCHRONOUS
# import pandas as pd
# from config import config

# url = config.influxdb_url
# username = config.influxdb_username
# password = config.influxdb_password
# token = f'{username}:{password}'

# database = 'input'
# retention_policy = 'autogen'
# bucket = f'{database}/{retention_policy}'

# client = InfluxDBClient(url=url, token=token)
# write_api = client.write_api(write_options=SYNCHRONOUS)
# query_api = client.query_api()

# def store_csv(csv='C:/Users/jan-n_palfbg6/OneDrive - bwedu/000 Uni/7. Semester/BA/CNC/Code/MLDeploy/cnc/CSV_SDMflex/SDMflex_V2_Training_final.csv', url='http://influxdb:8086/query'):
#     with write_api as _write_client:
#         _write_client.write('features/autogen','wbk', record={'measurement':'features', 'fields':{'feature':2}, 'time': 20})
#     # for df in pd.read_csv(csv, chunksize=1_000):

#     #     write_api.write(
#     #         record=df,
#     #         org='http://influxdb:8086/',
#     #         bucket="mydb2",
#     #         data_frame_measurement_name="stocks",
#     #         data_frame_tag_columns=["symbol"])
#     #         # ,
#     #         # data_frame_timestamp_column="date",
#     #     #)
#     # print('CSV is stored in InfluxDB')


# if __name__=='__main__':
#     store_csv()




from influxdb import InfluxDBClient
from datetime import datetime

myquery = f'from(bucket: "mydb")\
|> range(start: -10m)\
|> filter(fn: (r) => r._measurement == "sim_sensor")\
|> filter(fn: (r) => r["_field"] == "value")'

#Setup database
client = InfluxDBClient('localhost', 8086, 'admin', 'Password1', 'mydb')
client.create_database('mydb')
list = client.get_list_database()
client.switch_database('mydb')

# query_api = client.query_api()
# query = 'from(bucket:"my-bucket")\
# |> range(start: -10m)\
# |> filter(fn:(r) => r._measurement == "my_measurement")\
# |> filter(fn:(r) => r.location == "Prague")\
# |> filter(fn:(r) => r._field == "temperature")'



#Setup Payload
json_payload = []
data = {
    "measurement": "stocks",
    "tags": {
        "ticker": "TSLA"
        },
    "time": datetime.now(),
    "fields": {
        'open': 688.37,
        'close': 667.93
    }
}
json_payload.append(data)


#Send our payload
client.write(json_payload)


# Select statement
#result = client.query(query=myquery)

#print (list)
#print(result)
