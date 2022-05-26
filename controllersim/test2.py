class Section():
    def __init__(self, options):
        self.__setattr__(options[0], Option(options[1], options[2]))

    def add_option(self, name, type, fallback):
        self.__setattr__(name, Option(type, fallback))
        

class Option():
    def __init__(self, type, fallback):
        self.type = type
        self.fallback = fallback
        self.value = None

MQTT = Section(('test', str, 'abc'))
MQTT.add_option('broker_ip', str, 'localhost')
MQTT.add_option('broker_port', int, 1883)

if __name__ == '__main__':
    print(MQTT)