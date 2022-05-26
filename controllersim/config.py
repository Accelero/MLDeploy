from configtools import *

class MQTT(Section):
    broker_ip = Option(str)
    broker_port = Option(int)


class TEST(Section):
    test_var = Option(str)
    

manager = ConfigManager()