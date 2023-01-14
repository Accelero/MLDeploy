import grpc
import proto.ProcessLogDataProvider_pb2_grpc as pdp
import proto.ProcessLogConfiguration_pb2 as pc
import proto.ProtoProcessLogEntryContainer_pb2 as pe
import time
import signal
from datetime import datetime
import threading
import paho.mqtt.client as mqtt
import asyncio
import json
import numpy as np
import sys

from config import config

stop_event = threading.Event()


sensor_name = 1
sample_interval = float(config.get('SENSOR_' + str(sensor_name), 'sample_interval'))
send_interval = float(config.get('SENSOR_' + str(sensor_name), 'send_interval'))
pos = int(config.get('SENSOR_' + str(sensor_name), 'pos'))
buffer_size = int(config.get('SENSOR_' + str(sensor_name), 'buffer_size'))
tab = eval('pe.ProtoProcessLogEntryDataWert.' + config.get('SENSOR_' + str(sensor_name), 'tab_name'))
resolution_value = int(config.get('SENSOR_' + str(sensor_name), 'resolution'))


mqtt_topic = config.get('MQTT', 'topic')

pos_list = [pos]
# pos_list = [58228, 28077, 28078, 87005, 87006]

buffer = []

def make_process_log_configuration():

    parameters = [
        pc.Parameter(
                tab=tab,
                pos=pos,
                resolutions=[
                    pc.Resolution(value=resolution_value)
                ]
            ) for pos in pos_list]
    process_log_configuration = pc.ProcessLogConfiguration(  
        parameters=parameters
    )
    return process_log_configuration

def request_process_log_data_stream(stub):
    containers = stub.RequestProcessLogDataStream(
        make_process_log_configuration())
    return containers

def postprocess(container):
    global buffer
    arr = []
    for entry in container.entries:
        arr.append([
        *[data.protoWert.mFloat for data in entry.protoProcessLogData]])
    arr = np.array(arr)
    if len(buffer) == 0:
        buffer = arr
    else:
        buffer = np.vstack((np.array(buffer), arr))
    if len(buffer) > 0:
        buffer = buffer[-buffer_size:, :]
    buffer = buffer.tolist()



def start_request():
    print('gRPC request started...')
    channel = grpc.insecure_channel('localhost:59001')
    stub = pdp.ProcessLogDataProviderStub(channel)
    containers = request_process_log_data_stream(stub)
    return containers

def do_request(containers): # blocking
    try:
        while not stop_event.is_set():
            postprocess(next(containers))
    except Exception as e:
        print(e)
        

def stop_request(containers):
    containers.cancel()
    print('gRPC request cancelled!')
    
def run_grpc_client(containers):
    do_request(containers)

def sample_func(time_stamp):
    global buffer
    if len(buffer) == 0:
        # print('gRPC still no value')
        return
    sample_value = buffer.pop(0)[0]
    return time_stamp, sample_value

def signal_handler(containers, grpc_client_thread):
    stop_event.set()


if __name__ == '__main__':
    try:
        pos_list = [int(sys.argv[1])]
    except:
        pass
    stop_event.clear()
    
    # grpc
    containers = start_request()
    grpc_client_thread = threading.Thread(target=lambda: run_grpc_client(containers))
    signal.signal(signal.SIGINT, lambda signal, frame: signal_handler(containers, grpc_client_thread))

    grpc_client_thread.setDaemon(True)
    grpc_client_thread.start()


    # Setup MQTT Client (Emitting side)
    mqtt_client = mqtt.Client(protocol=mqtt.MQTTv5)
    def on_connect_fail(client, userdata):
        print('Sensor %s: MQTT Connection failed' % sensor_name)
    def on_connect(client, userdata, flags, reasonCode, properties):
        if reasonCode == 0:
            print('Sensor %s: MQTT connected' % sensor_name)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_connect_fail = on_connect_fail
    try:
        mqtt_client.connect(host='localhost', port=1883)
    except: pass
    mqtt_client.loop_start()

    # Setup sample and send loops. 
    # Asyncio loop runs sample and loop task until they're complete. 
    # The loops only complete, when the stop_event is set. 
    # Asyncio.gather is used to start the sleep at the same time as the coroutine, 
    # other than runnning the coroutine and then sleep afterwards. 
    output = []

    async def sample_loop():
        async def sample_coro():
            time_stamp = time.time()
            try:
                time_stamp, sample_value = sample_func(time_stamp)
            except:
                return

            print("pos: %s, time: %s, value: %s, remaining %s" % (pos,
                datetime.utcfromtimestamp(time_stamp), sample_value, len(buffer)))
            output.append({'time': time_stamp, 'value': sample_value})
            return
        while not stop_event.is_set():
            await asyncio.gather(asyncio.sleep(sample_interval), sample_coro())

    async def send_loop():
        async def send_coro():
            payload = json.dumps(output)
            output.clear()
            mqtt_client.publish(topic=mqtt_topic, payload=payload)
            return
        while not stop_event.is_set():
            await asyncio.gather(asyncio.sleep(send_interval), send_coro())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.gather(sample_loop(), send_loop()))
    mqtt_client.loop_stop()
    print("Sensor %s: MQTT stopped" % sensor_name)

    stop_request(containers)
    grpc_client_thread.join()