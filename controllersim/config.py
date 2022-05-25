from configparser import ConfigParser


class Section():
    pass


class Option():
    def __init__(self, type, fallback=None):
        self.type = type
        self.fallback = fallback
        self.value = None


class MQTT(Section):
    broker_ip = Option(str)
    broker_port = Option(int)


class TEST(Section):
    test_var = Option(str)


def load(file_path):
    _parser = ConfigParser()
    _parser.read(file_path)
    for key, val in list(globals().items()):
        if hasattr(val, '__base__'):
            if val.__base__ == Section:
                for k, v in list(val.__dict__.items()):
                    if isinstance(v, Option):
                        if v.type == str:
                            v.value = _parser.get(key, k)
                        if v.type == int:
                            v.value = _parser.getint(key, k)
                        if v.type == float:
                            v.value = _parser.getfloat(key, k)
                        if v.type == bool:
                            v.value = _parser.getboolean(key, k)


def save(file_path):
    _parser = ConfigParser()
    for key, val in list(globals().items()):
        if hasattr(val, '__base__'):
            if val.__base__ == Section:
                for k, v in list(val.__dict__.items()):
                    if isinstance(v, Option):
                        if not _parser.has_section(key):
                            _parser.add_section(key)
                        _parser.set(key, k, str(v.value))
    with open(file_path, 'w') as configfile:
        _parser.write(configfile)


if __name__ == '__main__':
    load('configtest/config.ini')
    print(MQTT.broker_ip.value)
