import config

config.manager.load('config.ini')

if __name__ == '__main__':
    print(config.MQTT.broker_port.get())