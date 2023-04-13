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

def deriv(x2_, y2_, i, n=0, back=1):
    if n == 0:
        return y2_[i]
    delta_x2_ = x2_[i] - x2_[i - back]
    if type(delta_x2_) == timedelta:
        delta_x2_ = delta_x2_.total_seconds()
    if delta_x2_ < 0:
        raise ValueError('delta_x2_ should be positive!')
    if delta_x2_ == 0:
        raise ZeroDivisionError('delta_x2_ is 0!')
    if n == 1:
        delta_y2_ = y2_[i] - y2_[i - back]
    else:
        delta_y2_ = deriv(x2_, y2_, i, n=n-1) - deriv(x2_, y2_, i - 1, n=n-1)
    return delta_y2_ / delta_x2_

def deriv_array(x2_, y2_, n=1, back=1):
    x2_n_ = []
    y2_n_ = []
    for i in range(len(x2_) - n):
        try:
            y2_n_.append(deriv(x2_, y2_, i + n, n=n, back=back))
            x2_n_.append(x2_[i + n])
        except: pass
    y2_n_ = np.array(y2_n_)
    x2_n_ = np.array(x2_n_)
    return x2_n_, y2_n_

def preprocess(_input: pd.DataFrame):
    global feature_start
    global feature_end
    global global_time_stamp
    global global_feature

    # back = 10

    # boundary_filter = 200
    # boundary_upper = 50
    # boundary_lower = 20

    boundaries_absolute = [250, 700, 1150]
    deviation_NC = 25
    deviation_time = 5

    df = _input[_input['_tag']==value]
    df = df.reset_index(drop=True)

    df_assist = _input[_input['_tag']==assist]
    df_assist = df_assist.reset_index(drop=True)

    # df_timesecond = _input[_input['_tag']==timesecond]
    # df_timesecond = df_timesecond.reset_index(drop=True)

    if num > 0:
        # value
        x1 = np.array(df['_time'])
        y1 = np.array(df['_value'])
        # assist
        x2 = np.array(df_assist['_time'])
        y2 = np.array(df_assist['_value'])
        # timesecond --> datetime
        # if not timesecond == 'None':
        #     x3 = np.array(df_timesecond['_time'])
        #     y3 = np.array(df_timesecond['_value'])

        #     x1_idx = np.where(np.in1d(x3, x1))[0]
        #     x1_orig = x3[x1_idx] # system datetime
        #     x1 = y3[x1_idx] # given timestamp
        #     x1 = np.array([datetime.fromtimestamp(i, tz=pytz.utc) for i in x1]) # ---> given datetime

        #     x2_idx = np.where(np.in1d(x3, x2))[0]
        #     x2_orig = x3[x2_idx]
        #     x2 = y3[x2_idx]
        #     x2 = np.array([datetime.fromtimestamp(i, tz=pytz.utc) for i in x2])
        # else:
        #     x1_orig = x1
        #     x2_orig = x2

        # if len(x2) < back:
        #     raise RuntimeError('Not enough data for derivative!')

        # alternative 1: derivatives
        # x2_1, y2_1 = deriv_array(x2, y2, n=1, back=back)
        # split = []
        # ok = True
        # for i, s in enumerate(y2_1):
        #     if s > boundary_upper:
        #         if ok:
        #             if y2[i + 1] > boundary_filter:
        #                 split.append(i + 1)
        #                 ok = False
        #     if s < boundary_lower and s < 0:
        #         ok = True
        # split = np.array(split)[:2]
        # new_feature_start = x1_orig[x1 <= x2_1[split[0]]][0]
        # new_feature_end = x2_orig[x1 <= x2_1[split[1]]][0]

        # alternative 2: absolute values
        # split = []
        # for boundary_absolute in boundaries_absolute:
        #     s = np.where((y2 > boundary_absolute - deviation_NC) & (y2 < boundary_absolute + deviation_NC))[0]
        #     if len(s) > 0:
        #         split.append(s[len(s) // 2])
        # split = np.sort(split)
        # logging.info(split)
        # if len(split) < 1:
        #     raise RuntimeError("Start of feature does not exist!")
        # if len(split) < 2:
        #     raise RuntimeError("End of feature does not exist!")
        # start = np.where(x1 <= x2[split[-2]])[0][-1]
        # new_feature_start = x1[start] # new_feature_start = x1_orig[start]
        # end = np.where(x1 <= x2[split[-1]])[0][-1]
        # new_feature_end = x1[end] # new_feature_end = x1_orig[end]
        # df = df.iloc[start:end]
        
        split = []
        starts = np.array([]).astype(int)
        starts = np.concatenate((starts, np.where(
                    (y2 == 0)[:-1] * (y2[1:] > 0)
                )[0] + 1))
        ends = np.array([]).astype(int)
        ends = np.concatenate((ends, np.where(
                    (y2 > 0)[:-1] * (y2[1:] == 0)
                )[0]))

        if len(ends) > 0 and len(starts) == len(ends):
            start_ = starts[-1]
            end_ = ends[-1]
            split = np.array([start_, end_])
        print(split)

        start = split[0]
        new_feature_start = x1[start] # new_feature_start = x1_orig[start]
        end = split[1]
        new_feature_end = x1[end] # new_feature_end = x1_orig[end]
        df = df.iloc[start:end]

        if not feature_start is None and not feature_end is None:
            if (new_feature_start - feature_start).total_seconds() < deviation_time \
                or (new_feature_end - feature_end).total_seconds() < deviation_time:
                logging.info('This interval exists already!')
                return global_time_stamp, global_feature
        
        feature_start = new_feature_start
        feature_end = new_feature_end

        logging.info(f"feature_start: {feature_start}")
        logging.info(f"feature_end: {feature_end}")

        freq = (feature_end - feature_start) / num

        df.set_index('_time', inplace=True)
        new_time_index = pd.date_range(
            start=feature_start, end=feature_end, freq=freq, inclusive='right')
        df = df.groupby(new_time_index[new_time_index.searchsorted(
                    df.index, side='left')]).mean(numeric_only=True)
        df = df.reindex(index=new_time_index)
        df = df.interpolate(method='linear', limit_direction='both')
        time_stamp = df.index[0] + (df.index[-1] - df.index[0]) / 2
        global_time_stamp = time_stamp

        # scale the feature between 0 and 1
        feature = df['_value']
        feature_max = max(feature)
        feature_min = min(feature)
        feature = (feature - feature_min) / (feature_max - feature_min)
        feature = feature.to_csv(columns=['_value'], header=False, index=False)
        global_feature = feature

        return global_time_stamp, global_feature

    # if num > 0: # for discrete features
    #     if not df.iloc[0]['_value'] == 0:
    #         # logging.info('The first value is not 0!')
    #         if global_time_stamp is None or global_feature is None:
    #             raise RuntimeError('Complete feature does not exist at the beginning!')
    #         return global_time_stamp, global_feature
    #     start_idxs = df.index[df['_value'] > 0]
    #     if len(start_idxs) == 0:
    #         raise RuntimeError('No feature is found!')
    #     start_idx = start_idxs[0]
    #     zero_idxs = df.index[df['_value'] == 0]
    #     zero_idxs = zero_idxs[zero_idxs > start_idx]
    #     if len(zero_idxs) == 0:
    #         raise RuntimeError('Feature is not complete!')
    #     zero_idxs = zero_idxs[:-1][(zero_idxs[1:] - zero_idxs[:-1]) == 1] # continuity
    #     end_idx = zero_idxs[0]

    #     df = df.loc[start_idx:end_idx]
    #     df = df.reset_index(drop=True)

    #     new_feature_start = df.iloc[0]['_time']
    #     new_feature_end = df.iloc[-1]['_time']

    #     if new_feature_start == feature_start or new_feature_end == feature_end: # THIS COMPARISON DOES NOT WORK
    #         logging.info('This interval exists already!')
    #         return global_time_stamp, global_feature
        
    #     feature_start = new_feature_start
    #     feature_end = new_feature_end
    #     freq = (feature_end - feature_start) / num



    #     df.set_index('_time', inplace=True)
    #     new_time_index = pd.date_range(
    #         start=feature_start, end=feature_end, freq=freq, inclusive='right')
    #     df = df.groupby(new_time_index[new_time_index.searchsorted(
    #                 df.index, side='left')]).mean(numeric_only=True)
    #     df = df.reindex(index=new_time_index)
    #     df = df.interpolate(method='linear', limit_direction='both')
    #     time_stamp = df.index[0] + (df.index[-1] - df.index[0]) / 2
    #     global_time_stamp = time_stamp

    #     # scale the feature between 0 and 1
    #     feature = df['_value']
    #     feature_max = max(feature)
    #     feature_min = min(feature)
    #     feature = (feature - feature_min) / (feature_max - feature_min)
    #     feature = feature.to_csv(columns=['_value'], header=False, index=False)
    #     global_feature = feature

    #     return global_time_stamp, global_feature
    
    if not df.empty:
        df.set_index('_time', inplace=True)
        end = df.loc[df.index[0],'_stop']
        start = df.loc[df.index[0],'_start']
        new_time_index = pd.date_range(
            start=start, end=end, freq=frequency, inclusive='right')
        df = df.groupby(new_time_index[new_time_index.searchsorted(
            df.index, side='left')]).mean(numeric_only=True)
        df = df.reindex(index=new_time_index)
        df = df.interpolate(method='linear', limit_direction='both')
        df.index.name = '_time'
        time_stamp = df.index[-1]
        feature = df.to_csv(columns=['_value'], header=False, index=False)
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
