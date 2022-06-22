import pandas as pd
import json
import paho.mqtt.client as mqtt
from config import config
import random
import time
import signal

mqtt_broker_ip = config.get('DEFAULT', 'mqtt_broker_ip')
mqtt_sub_topic = config.get('DEFAULT', 'mqtt_pub_topic')
mqtt_pub_topic = config.get('DEFAULT', 'mqtt_sub_topic')

client = mqtt.Client(client_id=None, clean_session=True)

def on_connect(client, userdata, flags, rc):
    print("flags: " + str(flags) + "result code: " + str(rc))
    client.subscribe(topic=mqtt_sub_topic)
client.on_connect = on_connect

def on_subscribe(client, userdata, mid, granted_qos):
    print("mid: " + str(mid) + "granted qos: " + str(granted_qos))
client.on_subscribe = on_subscribe

def on_message(client, userdata, message):
    print('loss: ' + message.payload.decode())
client.on_message = on_message

client.connect(host=mqtt_broker_ip, port=1883)

exitFlag = False
def signalHandler(signum, frame):
    global exitFlag
    exitFlag = True

data_path = "C:/Users/David/Nextcloud/MA David/Datensätze/HELLER-Data-Full.csv"
df = pd.read_csv(data_path)
features = df.iloc[:, :-1]

signal.signal(signal.SIGINT, signalHandler)
client.loop_start()

while not exitFlag:
    jsonData = json.dumps(features.sample().values.tolist())
    client.publish(topic=mqtt_pub_topic, payload=jsonData, qos=2, retain=True)
    rndpart = random.random()
    constpart = 2
    time.sleep(constpart + rndpart*2)

client.loop_stop()