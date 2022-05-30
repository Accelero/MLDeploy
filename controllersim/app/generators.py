import samplers
import multiprocessing as mp
import paho.mqtt.client as mqtt
from config import config
import asyncio
import json
import time
import signal

mqtt_broker_ip = config.get('MQTT', 'broker_ip')
mqtt_broker_port = config.getint('MQTT', 'broker_port', fallback=1883)


class Sensor():
    def __init__(self, sample_interval, send_interval, mqtt_topic):
        self.sampler = samplers.SineSampler(freq=1, noise=0.2)
        self.process = mp.Process(target=self.run)
        self.stop_event = mp.Event()
        self.output = []
        self.sample_interval = sample_interval
        self.send_interval = send_interval
        self.mqtt_topic = mqtt_topic

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(host=mqtt_broker_ip, port=mqtt_broker_port)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(self.sample_coro(), self.send_coro()))

    async def sample_coro(self):
        async def sample_subcoro():
            time_stamp = time.time()
            sample_value = self.sampler.sample(time_stamp)
            sample = {'time': time_stamp, 'value': sample_value}
            self.output.append(sample)
            return
        while not self.stop_event.is_set():
            await asyncio.gather(sample_subcoro(), asyncio.sleep(self.sample_interval))

    async def send_coro(self):
        async def send_subcoro():
            payload = json.dumps(self.output)
            self.output.clear()
            self.mqtt_client.publish(topic=self.mqtt_topic, payload=payload)
            return
        while not self.stop_event.is_set():
            await asyncio.gather(send_subcoro(), asyncio.sleep(self.send_interval))

    def start(self):
        self.process.start()

    def stop(self):
        self.stop_event.set()
        self.process.join()

if __name__ == '__main__':
    sens1 = Sensor()
    sens1.start()
    time.sleep(10)
    sens1.stop()