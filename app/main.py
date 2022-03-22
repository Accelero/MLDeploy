# main function and entry point for the modelserver

import restapi
import mqttclient
import config

def main():


    #start flask server
    restapi.app.run(host='0.0.0.0', port=9000, debug=True)
    #start mqtt client
    mqttclient.client.loop_start()


if __name__ == '__main__':
    main()