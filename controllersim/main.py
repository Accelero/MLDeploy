import asyncio
import signal
from generator import SignalGenerator

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
shutdownEvent = asyncio.Event()
gen = SignalGenerator(0.01, 0.5)


def signalHandler(signum, frame):
    shutdownEvent.set()

async def main():
    gen.start()
    await shutdownEvent.wait()
    gen.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    loop.run_until_complete(main())