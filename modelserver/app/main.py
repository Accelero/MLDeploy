import asyncio
import signal
import os
import subprocess
import requests

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
shutdownEvent = asyncio.Event()


def signalHandler(signum, frame):
    loop.call_soon_threadsafe(shutdownEvent.set)


async def main():
    r = requests.models.Response()
    url = 'http://influxdb:8086/query'
    while r.status_code != 200:
        try:
            params = {'q':'CREATE SUBSCRIPTION modelserver ON features.autogen DESTINATIONS ALL \'http://modelserver:9000/\''}
            r = requests.post(url=url, params=params)
        except:
            pass
    r.status_code = None
    while r.status_code != 200:
        try:
            params = {'q':'CREATE DATABASE predictions'}
            r = requests.post(url=url, params=params)
        except:
            pass

    os.environ['FLASK_APP'] = 'restapi.py'
    os.environ['FLASK_ENV'] = 'development'
    flaskserver = subprocess.Popen(
        ['flask', 'run', '-h', '0.0.0.0', '-p', '9000'], shell=False)

    await shutdownEvent.wait()
    params = {'q':'DROP SUBSCRIPTION modelserver ON features.autogen'}
    requests.post(url=url, params=params)
    flaskserver.terminate()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    loop.run_until_complete(main())
