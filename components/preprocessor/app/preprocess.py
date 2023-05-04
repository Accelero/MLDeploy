# from influxdb_client import InfluxDBClient, Point
# from influxdb_client.client.write_api import SYNCHRONOUS
from config import config
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import threading
from rabbitmq_client import RabbitMQClient
from mylogging import logging
import pika
from func_timeout import func_set_timeout
import func_timeout
import numpy as np
import pytz

# import warnings
# from influxdb_client.client.warnings import MissingPivotFunction

# window
window_width = config.parser.get('General', 'window_width')
window_step = config.parser.get('General', 'window_step')
frequency = config.parser.get('General', 'frequency')

window_width = pd.to_timedelta(window_width)
window_step = pd.to_timedelta(window_step)
frequency = pd.to_timedelta(frequency)

num = int(config.parser.get('General', 'num'))
value = config.parser.get('General', 'value')
assist = config.parser.get('General', 'assist')
# timesecond = config.parser.get('General', 'timesecond')

# RabbitMQ subscriber
rabbitmq_broker_ip = config.parser.get('RabbitMQ', 'broker_ip')
rabbitmq_broker_port = config.parser.get('RabbitMQ', 'broker_port')
rabbitmq_backup_size = config.parser.get('RabbitMQ', 'backup_size')
rabbitmq_backup_size = float(rabbitmq_backup_size)

rabbitmq_consumer_exchange = config.parser.get('RabbitMQ', 'consumer_exchange')
rabbitmq_consumer_data_format = config.parser.get('RabbitMQ', 'consumer_data_format')
rabbitmq_consumer_topic = config.parser.get('RabbitMQ', 'consumer_topic')
rabbitmq_consumer = RabbitMQClient(rabbitmq_broker_ip, rabbitmq_broker_port, rabbitmq_backup_size)

rabbitmq_producer_exchange = config.parser.get('RabbitMQ', 'producer_exchange')
rabbitmq_producer = RabbitMQClient(rabbitmq_broker_ip, rabbitmq_broker_port, rabbitmq_backup_size)

# # Influxdb
# url = config.parser.get('Influxdb', 'url')
# database = config.parser.get('Influxdb', 'database')
# username = config.parser.get('Influxdb', 'username')
# password = config.parser.get('Influxdb', 'password')
# token = f'{username}:{password}'

# database = 'input'
# retention_policy = 'autogen'
# bucket = f'{database}/{retention_policy}'

# client = InfluxDBClient(url=url, token=token)
# write_api = client.write_api(write_options=SYNCHRONOUS)


# query_api = client.query_api()
# query = f'from(bucket: "{bucket}")\
# |> range(start: -{window_width})\
# |> filter(fn: (r) => r._measurement == "sim_sensor")\
# |> filter(fn: (r) => r["_field"] == "value")'


feature_start = None
feature_end = None

global_time_stamp = None
global_feature = None

stopEvent = threading.Event()

def rabbitmq_consumer_run():
    # consume
    logging.info('RabbitMQ cosumer connection starts...')
    start = datetime.now()
    rabbitmq_consumer.connect('preprocessor_consumer', is_consumer=True)
    rabbitmq_consumer.setup(rabbitmq_consumer_exchange)
    rabbitmq_consumer.subscribe(window_width, frequency, 
        rabbitmq_consumer_data_format, rabbitmq_consumer_topic)
    end = datetime.now()
    logging.info('RabbitMQ consumer connection takes %ss' % (end - start).total_seconds())
    rabbitmq_consumer.consume()


def rabbitmq_producer_run():
    # produce
    logging.info('RabbitMQ producer connection starts...')
    start = datetime.now()
    rabbitmq_producer.connect('preprocessor_producer', is_consumer=False)
    rabbitmq_producer.setup(rabbitmq_producer_exchange)
    end = datetime.now()
    logging.info('RabbitMQ producer connection takes %ss' % (end - start).total_seconds())

# This funtion is used to find feature ranges for continuous or discreate feature

def recap_df_continuous(df, df_assist):
    start = df.iloc[0]['_start']
    end = df.iloc[0]['_end']
    freq = frequency
    return df, start, end, freq

def recap_df_discrete(df, df_assist):
    start = None
    end = None
    freq = None
    try:
        # value
        x1 = np.array(df['_time'])
        y1 = np.array(df['_value'])
        # assist
        x2 = np.array(df_assist['_time'])
        y2 = np.array(df_assist['_value'])
        
        split = []
        start_idxs = np.array([]).astype(int)
        start_idxs = np.concatenate((start_idxs, np.where(
                    (y2 == 0)[:-1] * (y2[1:] > 0)
                )[0] + 1))
        end_idxs = np.array([]).astype(int)
        end_idxs = np.concatenate((end_idxs, np.where(
                    (y2 > 0)[:-1] * (y2[1:] == 0)
                )[0]))

        if len(end_idxs) > 0 and len(start_idxs) == len(end_idxs):
            start_idx_ = start_idxs[-1]
            end_idx_ = end_idxs[-1]
            if start_idx_ < end_idx_:
                split = np.array([start_idx_, end_idx_])
                

                start_idx = split[0]
                end_idx = split[1]
                df = df.iloc[start_idx:end_idx]

                start = x1[start_idx] # new_feature_start = x1_orig[start]
                end = x1[end_idx] # new_feature_end = x1_orig[end]
                freq = (end - start) / num
    except:
        pass

    return df, start, end, freq

def recap_df(df, df_assist, is_discrete):
    if not is_discrete:
        return recap_df_continuous(df, df_assist)
    else:
        return recap_df_discrete(df, df_assist)

def preprocess(_input: pd.DataFrame):
    # main df
    df = _input[_input['_tag']==value]
    df = df.reset_index(drop=True)
    # assist df
    df_assist = _input[_input['_tag']==assist]
    df_assist = df_assist.reset_index(drop=True)

    # find the start, end and freq
    is_discrete = True if num > 0 else False
    df, start, end, freq = recap_df(df, df_assist, is_discrete)

    if start is None or end is None or freq is None:
        raise ValueError("One of start, end or freq is None!")
    
    # interpolation of feature with evenly spaced intervals
    df.set_index('_time', inplace=True)
    new_time_index = pd.date_range(
        start=start, end=end, freq=freq, inclusive='right')
    df = df.groupby(new_time_index[new_time_index.searchsorted(
                df.index, side='left')]).mean(numeric_only=True)
    df = df.reindex(index=new_time_index)
    df = df.interpolate(method='linear', limit_direction='both')

    # scale feature between 0 and 1
    feature = df['_value']
    feature_max = max(feature)
    feature_min = min(feature)
    feature = (feature - feature_min) / (feature_max - feature_min)
    feature = feature.to_csv(columns=['_value'], header=False, index=False)

    # find timestamp
    time_stamp = df.index[0] + (df.index[-1] - df.index[0]) / 2

    return time_stamp, feature


@func_set_timeout(window_step.total_seconds())
def event():
    try:
        # get data by rabbitmq consumer
        if not rabbitmq_producer.connected:
            raise RuntimeError('RabbitMQ producer connecting to RabbitMQ broker')
        if not rabbitmq_consumer.connected:
            raise RuntimeError('RabbitMQ consumer connecting to RabbitMQ broker')
        logging.debug('Getting buffer from RabbitMQ broker...')
        # df = query_api.query_data_frame(query) # influxdb query
        buffer_full, buffer = rabbitmq_consumer.get_buffer()
        if not buffer_full and num == 0:
            # logging.warning('RabbitMQ consumer buffer not full!')
            raise RuntimeError('RabbitMQ consumer buffer not full, waiting...')
        time_stamp, feature = preprocess(buffer)
        record = {'measurement':'features', 'fields':{'feature':feature}, 'time':time_stamp}
        # send data by rabbitmq producer
        rabbitmq_producer.publish(json.dumps(record, default=str))
        logging.info(f'time {time_stamp} sent')
        # # persistent storage
        # with write_api as _write_client:
        #     _write_client.write(f'{}/autogen','wbk', record=record)
    except RuntimeError as e:
        logging.error('Runtime error: %s' % e)
    except Exception as e:
        logging.error(e)
def run():
    while not stopEvent.is_set():
        try:
            event()
        except func_timeout.exceptions.FunctionTimedOut as e: 
            logging.error('Time out error: %s' % e)
        time.sleep(window_step.total_seconds())
        # 1 thread: preprocessing in winow step
        # 1 thread: tick



rabbitmq_consumer_thread = threading.Thread(target=rabbitmq_consumer_run)
rabbitmq_producer_thread = threading.Thread(target=rabbitmq_producer_run)
preprocess_thread = threading.Thread(target=run)

def start():
    rabbitmq_consumer_thread.start()
    rabbitmq_producer_thread.start()
    preprocess_thread.start()

def stop():
    stopEvent.set()
    preprocess_thread.join()
    rabbitmq_consumer.disconnect()
    rabbitmq_producer.disconnect()

if __name__=='__main__':
    pass
