# main function and entry point for the modelserver

import restapi
import mqttclient
import config
import os
import subprocess

def main():

    os.environ['FLASK_APP'] = 'app/restapi.py'
    flaskserver = subprocess.Popen('flask run' + ' -p 9000')
    #start flask server
    # restapi.app.run(host='localhost', port=9000, debug=True)
    #start mqtt client
    print('test')
    mqttclient.client.loop_forever()


if __name__ == '__main__':
    main()