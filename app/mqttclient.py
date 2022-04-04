import paho.mqtt.client as mqtt
from config import config
import inference
import json

mqtt_client_id = config.get('DEFAULT', 'mqtt_client_id')
mqtt_broker_ip = config.get('DEFAULT', 'mqtt_broker_ip')
mqtt_broker_port = config.getint('DEFAULT', 'mqtt_broker_port')
mqtt_sub_topic = config.get('DEFAULT', 'mqtt_sub_topic')
mqtt_pub_topic = config.get('DEFAULT', 'mqtt_pub_topic')

if len(mqtt_client_id)==0 or mqtt_client_id == None:
    clean_session = True
else:
    clean_session = False
client = mqtt.Client(client_id=mqtt_client_id, clean_session=clean_session)

def on_connect(client, userdata, flags, rc):
    print("flags: " + str(flags) + "result code: " + str(rc))
client.on_connect = on_connect

def on_subscribe(client, userdata, mid, granted_qos):
    print("mid: " + str(mid) + "granted qos: " + str(granted_qos))
client.on_subscribe = on_subscribe

def on_message(client, userdata, message):
    response = inference.eval(json.loads(message.payload.decode('utf-8')))
    client.publish(topic=mqtt_pub_topic, payload=response, qos=2, retain=True)
client.on_message = on_message

client.enable_logger()
client.connect(host=mqtt_broker_ip, port=mqtt_broker_port)
client.subscribe(topic=mqtt_sub_topic)