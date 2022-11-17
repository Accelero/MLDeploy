import samplers
import multiprocessing as mp
import paho.mqtt.client as mqtt
from config import config
import asyncio
import json
import time
import signal
import logging


mqtt_broker_ip = config.get('MQTT', 'broker_ip')
mqtt_broker_port = config.getint('MQTT', 'broker_port', fallback=1883)


class Sensor():
    def __init__(self, name, sample_interval, send_interval, mqtt_topic):
        self.name = name
        self.sampler = samplers.SineSampler(freq=1, noise=0.2)
        self.process = mp.Process(target=self._run, name=self.name)
        self.stop_event = mp.Event()
        self.sample_interval = sample_interval
        self.send_interval = send_interval
        self.mqtt_topic = mqtt_topic
        logging.info("Sensor %s: spawned" % self.name)

    def _run(self):
        # Ignore SIGINT/keyboard interrupt on the subprocess
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Setup MQTT Client
        mqtt_client = mqtt.Client(protocol=mqtt.MQTTv5)
        def on_connect_fail(client, userdata):
            logging.warn('Sensor %s: MQTT Connection failed' % self.name)
        def on_connect(client, userdata, flags, reasonCode, properties):
            if reasonCode == 0:
                logging.info('Sensor %s: MQTT connected' % self.name)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_connect_fail = on_connect_fail
        try:
            mqtt_client.connect(host=mqtt_broker_ip, port=mqtt_broker_port)
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
                sample_value = self.sampler.sample(time_stamp)
                sample = {'time': time_stamp, 'value': sample_value}
                output.append(sample)
                return
            while not self.stop_event.is_set():
                await asyncio.gather(asyncio.sleep(self.sample_interval), sample_coro())

        async def send_loop():
            async def send_coro():
                payload = json.dumps(output)
                output.clear()
                mqtt_client.publish(topic=self.mqtt_topic, payload=payload)
                return
            while not self.stop_event.is_set():
                await asyncio.gather(asyncio.sleep(self.send_interval), send_coro())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(sample_loop(), send_loop()))
        mqtt_client.loop_stop()
        logging.info("Sensor %s: stopped" % (self.name))

    def start(self):
        self.stop_event.clear()
        self.process.start()

    # Currently the stop function blocks until the send and sample loops have finished 
    # the last iteration of the loop. A non-blocking implementation would be better. 
    def stop(self):
        self.stop_event.set()
        # logging.info("Sensor %s: stopped" % (self.name))

if __name__ == '__main__':
    pass