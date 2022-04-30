import random
import time
import math
import asyncio
import paho.mqtt.client as mqtt
import json
import threading

def generateSineSample(start_time, ampl=1, freq=10, phase=0, offset=1, noise=0):
    time_stamp = time.time()
    signal = ampl*math.sin((time_stamp - start_time)*2*math.pi*freq+phase)+offset
    rand_noise = random.uniform(-noise, noise)
    value = signal + rand_noise
    sample = {'time':time_stamp, 'value':value}
    return sample

class SignalGenerator():
    def __init__(self, sample_interval, send_interval):
        self.sample_interval = sample_interval
        self.send_interval = send_interval
        self.thread = threading.Thread(target=self.run)
        self.mqttClient = mqtt.Client()
        self.mqttClient.connect(host='localhost', port=1883)
        self.output = []

    async def sample(self, start_time, interval):
        while not self.stopEvent.is_set():
            self.output.append(generateSineSample(start_time, freq=1))
            await asyncio.sleep(interval)

    async def send(self, interval):
        while not self.stopEvent.is_set():
            payload = json.dumps(self.output)
            self.mqttClient.publish(topic='sim_sensor', payload=payload)
            self.output.clear()
            await asyncio.sleep(interval)

    def run(self): 
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.stopEvent = asyncio.Event()
        self.loop.create_task(self.sample(time.time(), self.sample_interval))
        self.loop.run_until_complete(self.send(self.send_interval))

    def start(self):
        self.thread.start()

    def stop(self):
        self.loop.call_soon_threadsafe(self.stopEvent.set)
        self.thread.join()


if __name__=='__main__':
    gen = SignalGenerator(0.01, .05)
    gen.start()
    time.sleep(2)
    gen.stop()