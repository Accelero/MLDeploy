from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import config
import pandas as pd
import time
import threading

url = config.influxdb_url
username = config.influxdb_username
password = config.influxdb_password
token = f'{username}:{password}'

database = 'input'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

client = InfluxDBClient(url=url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

query = f'from(bucket: "{bucket}")\
|> range(start: -{config.window_width})\
|> filter(fn: (r) => r._measurement == "sim_sensor")\
|> filter(fn: (r) => r["_field"] == "value")'

stopEvent = threading.Event()

def preprocess(input: pd.DataFrame):
            df = input
            if not df.empty:
                df.set_index('_time', inplace=True)
                end = df.loc[df.index[0],'_stop']
                start = df.loc[df.index[0],'_start']
                new_time_index = pd.date_range(
                    start=start, end=end, freq='50ms', inclusive='right')
                df = df.groupby(new_time_index[new_time_index.searchsorted(
                    df.index, side='left')]).mean()
                df = df.reindex(index=new_time_index)
                df = df.interpolate(method='linear', limit_direction='both')
                df.index.name = '_time'

                df.drop(df.columns.difference(['_value']), axis=1, inplace=True)
                time_stamp = df.index[-1]
                feature = df.to_csv(columns=['_value'], header=False, index=False)
                
                return time_stamp, feature


def resample(df: pd.DataFrame):
    df.set_index('_time', inplace=True)
    series = df['_value'].squeeze()
    if isinstance(series, pd.Series):
        window_start = series.index[-1] - pd.to_timedelta('5s')
        print(window_start)
        series = series.reindex(series.index.insert(series.index.searchsorted(window_start), window_start), method=None)
        series.interpolate(method='time', limit_direction='both', inplace=True)
        series.drop(series[series.index < window_start].index, inplace=True)
        print(series)
        print(series.resample('50 ms', origin='end', closed='right', label='right').mean())
    else:
        raise TypeError('Dataframe has wrong structure')


def run():
    while not stopEvent.is_set():
        try:
            df = query_api.query_data_frame(query)
            time_stamp, feature = preprocess(df)
            with write_api as _write_client:
                _write_client.write('features/autogen','wbk', record={'measurement':'features', 'fields':{'feature':feature}, 'time': time_stamp})

        except:
            pass
        time.sleep(pd.to_timedelta(config.window_step).total_seconds())
        

preprocess_thread = threading.Thread(target=run)

def start():
    preprocess_thread.start()

def stop():
    stopEvent.set()

if __name__=='__main__':
    df = query_api.query_data_frame(query)
    resample(df)
    # print(a, b, len(b), sep='\n')