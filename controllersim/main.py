import asyncio
import signal
from generator import SignalGenerator

# setup logging
import logging


def warning_filter(record: logging.LogRecord):
    if record.levelno >= 30:
        return False
    return True


formatter = logging.Formatter(
    '%(asctime)s %(levelname)-7s %(module)-20s %(message)s')

stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(formatter)
stderr_handler.setLevel(logging.WARNING)

stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.addFilter(warning_filter)

logging.basicConfig(
    handlers=[stderr_handler, stdout_handler], level=logging.INFO)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
shutdownEvent = asyncio.Event()
gen = SignalGenerator(0.01, 0.01)


def signal_handler(signum, frame):
    shutdownEvent.set()


async def main():

    logging.warning('test')
    gen.start()
    await shutdownEvent.wait()
    gen.stop()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    loop.run_until_complete(main())
