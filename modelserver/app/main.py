# main function and entry point for the modelserver

import mqttclient
import threading
import os
import subprocess
import signal

shutdownFlag = threading.Event()


def signalHandler(signum, frame):
    shutdownFlag.set()


def main():

    os.environ['FLASK_APP'] = 'app/restapi.py'
    os.environ['FLASK_ENV'] = 'development'
    flaskserver = subprocess.Popen(
        ['flask', 'run', '-h', 'localhost', '-p', '9000'], shell=False)
    # restapi.app.run(host='0.0.0.0', port=9000, debug=False)

    mqttclient.client.loop_start()

    while not shutdownFlag.wait(1):
        pass

    flaskserver.terminate()
    mqttclient.client.loop_stop()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    main()
