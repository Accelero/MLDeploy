from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

username = 'egal'
password = 'egal'
token = f'{username}:{password}'

database = 'input'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

url = 'http://localhost:8086'
client= InfluxDBClient(url=url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

query = f'from(bucket: "{bucket}") |> range(start: -10h)\
|> filter(fn: (r) => r["_field"] == "value")'

print(query_api.query(query))
# /query?db=&q=CREATE+SUBSCRIPTION+%22kapacitor-124fe1dc-ef56-4fab-92d5-89ef0ae63683%22+ON+mydb.test+DESTINATIONS+ANY+%27http%3A%2F%2Fe8c3ff2ee0f4%3A9092%27