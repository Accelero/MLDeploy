import paho.mqtt.client as mqtt
from config import config


mqtt_broker_ip = config.get('DEFAULT', 'mqtt_broker_ip')
mqtt_broker_port = config.getint('DEFAULT', 'mqtt_broker_port')

print('creating mqtt client instance')
client = mqtt.Client(client_id='testclient')

print('connecting to broker')
client.connect(host=mqtt_broker_ip, port=mqtt_broker_port)

print('subscribing to topic feature_store/machine1/feature_vectors')
client.subscribe(topic='feature_store/machine1/feature_vectors')

def on_message(client, userdata, message):
    print('Received message' + str(message.payload))

client.on_message = on_message

print('starting client')
client.loop_start()