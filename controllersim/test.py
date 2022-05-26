import config
from multiprocessing import Process
import os

config.load('config.ini')

def foo(test):
    print(f'{os.getpid()} {test.get()}')
    test.set(str(os.getpid()))
    print(test.get())

p1 = Process(target=foo, args=(config.MQTT.broker_ip,))
p2 = Process(target=foo, args=(config.MQTT.broker_ip,))
p3 = Process(target=foo, args=(config.MQTT.broker_ip,))

if __name__ == '__main__':
    p1.start()
    p2.start()
    p3.start()
    config.save('config.ini')