from flask import Flask, request, Response
import inference
from line_protocol_parser import parse_line
import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

app = Flask(__name__.split('.')[0])

url = 'http://influxdb:8086'
username = ''
password = ''
token = f'{username}:{password}'

database = 'features'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

client = InfluxDBClient(url=url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

def parse(input_data):
    dict_data = parse_line(input_data)
    time_stamp = dict_data['time']
    feature = np.fromstring(dict_data['fields']['feature'], sep='\n', dtype=np.float32)
    feature = np.reshape(feature, (1,100))
    return time_stamp, feature


@app.route('/write', methods=['POST'])
def evalloss():
    time_stamp, feature = parse(request.data)
    loss = inference.eval(feature)
    with write_api as _write_client:
        _write_client.write('predictions/autogen','wbk', record={'measurement':'prediction', 'fields':{'loss':loss.item()}, 'time': time_stamp})
    return Response(status=200)
