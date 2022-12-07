from influxdb_client import InfluxDBClient
import pandas as pd
import numpy as np
import time
import logging
import asyncio
from skmultiflow.drift_detection.adwin import ADWIN

'''
Setup event loop to repeat the detection.
'''
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

'''
Use logger to print info in container dashboard.
'''
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('')

handler.setFormatter(formatter)
logger.addHandler(handler)

'''
Setup the influxDB python client
'''
username = "telegraf"
password = "telegraf123"
token = f'{username}:{password}'

database = 'input'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

url = 'http://influxdb:8086'
client = InfluxDBClient(url=url, token=token)

query_api = client.query_api()


async def busy_loop():
    while True:
        await asyncio.sleep(3)
        test_query()


def test_query():

    query = 'from(bucket:"input/autogen")\
    |> range(start: -3s)\
    |> filter(fn: (r) => r._measurement == "sim_sensor")\
    |> filter(fn: (r) => r["_field"] == "value")\
    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")'

    query_result = query_api.query_data_frame(query=query)
    result_as_array = query_result[["value"]].to_numpy().tolist()
    
    logger.info(result_as_array)

    not_detected = 'not detected'

    adwin = ADWIN()
    for i in range(len(result_as_array)):
        adwin.add_element(result_as_array[i][0])
        if adwin.detected_change():
            logger.info('detected!!')
            not_detected = ''
    logger.info(not_detected)


def main():
    loop.run_until_complete(busy_loop())


if __name__ == "__main__":
    main()