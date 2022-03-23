# main function and entry point for the modelserver

from multiprocessing.connection import wait
import restapi
import mqttclient
import config
import os
import subprocess
import signal
import time

isRunning = bool
def signalHandler(signum, frame):
    global isRunning
    isRunning = False

def main():
    global isRunning
    isRunning = True
    os.environ['FLASK_APP'] = 'restapi.py'
    # p = subprocess.Popen(['flask', 'run', '-h', '0.0.0.0', '-p', '9000'], shell=False)
    # restapi.app.run(host='0.0.0.0', port=9000, debug=False)
    mqttclient.client.loop_start()
    while isRunning:
        time.sleep(1)
    mqttclient.client.loop_stop()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signalHandler)
    main()