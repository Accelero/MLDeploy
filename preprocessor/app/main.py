import asyncio
import signal
import preprocess
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
            params = {'q':'CREATE DATABASE features'}
            r = requests.post(url=url, params=params)
        except:
            pass

    preprocess.start()

    await shutdownEvent.wait()

    preprocess.stop()
    preprocess.preprocess_thread.join()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    loop.run_until_complete(main())
