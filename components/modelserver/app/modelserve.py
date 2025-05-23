import inference
from func_timeout import func_set_timeout
import func_timeout
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from config import config
from rabbitmq_client import RabbitMQClient
from mylogging import logging
from datetime import datetime
import threading
import numpy as np
import pandas as pd
import json
import time
import pika

## CONFIGURATION
# general
window_step = config.parser.get('General', 'window_step')
window_step = pd.to_timedelta(window_step)
# RabbitMQ client - general
rabbitmq_broker_ip = config.parser.get('RabbitMQ', 'broker_ip')
rabbitmq_broker_port = config.parser.get('RabbitMQ', 'broker_port')
rabbitmq_backup_size = config.parser.get('RabbitMQ', 'backup_size')
rabbitmq_backup_size = float(rabbitmq_backup_size)
# RabbitMQ client - consumer
rabbitmq_consumer_exchange = config.parser.get('RabbitMQ', 'consumer_exchange')
rabbitmq_consumer = RabbitMQClient(rabbitmq_broker_ip, rabbitmq_broker_port, rabbitmq_backup_size)
# RabbitMQ client - producer
rabbitmq_producer_exchange = config.parser.get('RabbitMQ', 'producer_exchange')
rabbitmq_producer = RabbitMQClient(rabbitmq_broker_ip, rabbitmq_broker_port, rabbitmq_backup_size)
# Influxdb
url = config.parser.get('Influxdb', 'url')
database = config.parser.get('Influxdb', 'database')
username = config.parser.get('Influxdb', 'username')
password = config.parser.get('Influxdb', 'password')
token = f'{username}:{password}'
client = InfluxDBClient(url=url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)

# stop event
stopEvent = threading.Event()

# ---------------------------------------------------------------- THREADS / INFRASTRUCTURE ----------------------------------------------------------------
def rabbitmq_consumer_run():
    # consume
    logging.info('RabbitMQ cosumer connection starts...')
    start = datetime.now()
    rabbitmq_consumer.connect('modelserver_consumer', is_consumer=True)
    rabbitmq_consumer.setup(rabbitmq_consumer_exchange)
    rabbitmq_consumer.subscribe()
    end = datetime.now()
    logging.info('RabbitMQ consumer connection takes %ss' % (end - start).total_seconds())
    rabbitmq_consumer.consume()
def rabbitmq_producer_run():
    # produce
    logging.info('RabbitMQ producer connection starts...')
    start = datetime.now()
    rabbitmq_producer.connect('modelserver_producer', is_consumer=False)
    rabbitmq_producer.setup(rabbitmq_producer_exchange)
    end = datetime.now()
    logging.info('RabbitMQ producer connection takes %ss' % (end - start).total_seconds())

# ---------------------------------------------------------------- CORE FUNCTIONS ----------------------------------------------------------------
# deserialization
def parse(input_data):
    dict_data = json.loads(input_data)
    time_stamp = dict_data['time']
    feature = np.fromstring(dict_data['fields']['feature'], sep='\n', dtype=np.float32)
    feature = np.reshape(feature, (1, -1))
    return time_stamp, feature
# core function with timeout for thread function 3: interefence with ML-algorithm and write to database
@func_set_timeout(window_step.total_seconds())
def evalloss():
    try:
        # get data by rabbitmq consumer
        # if not rabbitmq_producer.connected:
        #     raise RuntimeError('RabbitMQ producer connecting to RabbitMQ broker')
        if not rabbitmq_consumer.connected:
            raise RuntimeError('RabbitMQ consumer connecting to RabbitMQ broker')
        logging.debug('Getting buffer from RabbitMQ broker...')
        time_stamp, feature = parse(rabbitmq_consumer.body)
        loss = inference.eval(feature)
        logging.info(f'time {time_stamp} loss {loss} calculated!')
        record = {'measurement':'prediction', 'fields':{'loss':loss.item()}, 'time': time_stamp}
        # send data by rabbitmq producer
        # rabbitmq_producer.publish(json.dumps(record, default=str))
        # persistent storage
        with write_api as _write_client:
            _write_client.write(f'{database}/autogen','wbk', record=record)
    except RuntimeError as e:
        logging.error('Runtime error: %s' % e)
    except: pass
# thread function 3
def run():
    while not stopEvent.is_set():
        try:
            evalloss()
        except func_timeout.exceptions.FunctionTimedOut as e: 
            logging.error('Time out error: %s' % e)
# create threads
rabbitmq_consumer_thread = threading.Thread(target=rabbitmq_consumer_run)
# rabbitmq_producer_thread = threading.Thread(target=rabbitmq_producer_run)
modelserve_thread = threading.Thread(target=run)
# start threads
def start():
    rabbitmq_consumer_thread.start()
    # rabbitmq_producer_thread.start()
    modelserve_thread.start()
# stop threads
def stop():
    stopEvent.set()
    modelserve_thread.join()
    rabbitmq_consumer.disconnect()
    # rabbitmq_producer.disconnect()
