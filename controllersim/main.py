import asyncio
import signal
from generator import SignalGenerator
import threading
import time

loop = asyncio.new_event_loop()
gen = SignalGenerator(0.01, 0.5)

def signalHandler(signum, frame):
    print('signal received')
    shutdownEvent.set()

async def main():
    global shutdownEvent
    shutdownEvent = asyncio.Event()
    gen.start()
    print('started')
    await shutdownEvent.wait()
    print('shutting down')
    gen.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    asyncio.run(main())