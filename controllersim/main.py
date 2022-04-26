import asyncio
import signal

shutdownEvent = asyncio.Event()

def signalHandler(signum, frame):
    shutdownEvent.set()
    print('stopping')

async def main():
    print('main started')
    await shutdownEvent.wait()
    print('main finished')

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())