import asyncio
import signal
import requests
import modelserve
from config import config

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
shutdownEvent = asyncio.Event()


def signalHandler(signum, frame):
    loop.call_soon_threadsafe(shutdownEvent.set)


async def main():
    r = requests.models.Response()
    url = config.parser.get('Influxdb', 'url') + '/query'
    while r.status_code != 200 and not shutdownEvent.is_set():
        try:
            params = {'q':'CREATE DATABASE predictions'}
            r = requests.post(url=url, params=params, timeout=1)
        except:
            pass

    modelserve.start()
    await shutdownEvent.wait()
    modelserve.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    loop.run_until_complete(main())
