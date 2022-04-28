import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect(host='localhost')
payload = 'sim_sensor value=1.2'

client.publish(topic='sim_sensor', payload=payload)

client.publish(topic='sim_sensor', payload=payload)

client.publish(topic='sim_sensor', payload=payload)

client.publish(topic='sim_sensor', payload=payload)

client.publish(topic='sim_sensor', payload=payload)

