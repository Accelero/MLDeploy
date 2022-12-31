# setup logging
import logging
import sys

def warning_filter(record: logging.LogRecord):
    if record.levelno >= 30:
        return False
    return True


debug_formatter = logging.Formatter(
    '%(asctime)s %(levelname)-7s %(module)-20s %(message)s')

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(debug_formatter)
stderr_handler.setLevel(logging.WARNING)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(debug_formatter)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.addFilter(warning_filter)

logging.basicConfig(
    handlers=[stderr_handler, stdout_handler], level=logging.INFO)

import asyncio
import signal
import generators
from config import config

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
shutdownEvent = asyncio.Event()


def signal_handler(signum, frame):
    shutdownEvent.set()

def startup():
    global sensors
    sensors = []
    sections = config.sections()
    for section in sections:
        if section.startswith('SENSOR_'):
            name = section.removeprefix('SENSOR_')
            sample_interval = config.getfloat(section, 'sample_interval')
            send_interval = config.getfloat(section, 'send_interval')
            mqtt_topic = config.get(section, 'mqtt_topic')
            sensors.append(generators.Sensor(name, sample_interval, send_interval, mqtt_topic))

    for sensor in sensors:
        sensor.start()

def shutdown():
    for sensor in sensors:
        sensor.stop()

async def main():
    startup()
    await shutdownEvent.wait()
    shutdown()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logging.info('controllersim')
    loop.run_until_complete(main())
