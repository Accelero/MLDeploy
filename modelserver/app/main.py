import asyncio
import signal
import os
import subprocess

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
shutdownEvent = asyncio.Event()


def signalHandler(signum, frame):
    loop.call_soon_threadsafe(shutdownEvent.set)


async def main():

    os.environ['FLASK_APP'] = 'restapi.py'
    os.environ['FLASK_ENV'] = 'development'
    flaskserver = subprocess.Popen(
        ['flask', 'run', '-h', '0.0.0.0', '-p', '9000'], shell=False)

    await shutdownEvent.wait()

    flaskserver.terminate()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    loop.run_until_complete(main())
