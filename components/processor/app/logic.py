# test processor logic
# 1. check rabittmq_consumer: telegraf producer (rabbitmq client) --> TEMPLATE_PROCESSOR_consumer
# 2. check rabittmq_producer: TEMPLATE_PROCESSOR_consumer --> TEMPLATE_PROCESSOR_producer
# 3. check influxdb sender: TEMPLATE_PROCESSOR_consumer --> influxdb_sender (sink)
# 4. check influxdb receicer: influxdb_sender --> influxdb_receiver

from config import config
from mylogging import logging

import pandas as pd
import json

def logic_fun(rabbitmq_consumer, rabbitmq_producer, sender_client, receiver_client,
              window_width, window_step, frequency):
    # get data by rabbitmq consumer
    if not rabbitmq_producer.connected:
        raise RuntimeError('RabbitMQ producer connecting to RabbitMQ broker')
    if not rabbitmq_consumer.connected:
        raise RuntimeError('RabbitMQ consumer connecting to RabbitMQ broker')
    logging.debug('Getting buffer from RabbitMQ broker...')
    
    # 1. check: buffer in df
    _, buffer = rabbitmq_consumer.get_buffer()
    logging.info(f'Data received from Telegraf over RabbitMQ consumer:\n{buffer}')
    # 2. check: body in json
    average_value = buffer['_value'].mean()
    average_time = buffer['_time'].mean()
    record = {'fields':{'average':average_value}, 'time':average_time}
    rabbitmq_producer.publish(json.dumps(record, default=str))
    logging.info(f'record = {record} sent to RabbitMQ producer')
    # 3. check
    fields = {'average':average_value}
    sender_client.write(fields, average_time)
    logging.info(f'fields:{fields} at time {average_time} sent to InfluxDB')
    # 4. check
    received_res = receiver_client.get_query(window_width, 'average')
    logging.info(f'Received response from InfluxDB:\n{received_res}')