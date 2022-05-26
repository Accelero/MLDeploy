from configparser import ConfigParser
from multiprocessing import Value, Array, sharedctypes


class Section():
    pass


class Option():
    def __init__(self, type, fallback=None):
        self.type = type
        self.fallback = fallback
        self.value = None

    def get(self):
        if isinstance(self.value, sharedctypes.SynchronizedString):
            return self.value.value.decode()
        else:
            return self.value.value

    def set(self, value):
        try:
            if isinstance(self.value, sharedctypes.SynchronizedString):
                self.value.value = bytes(value, 'utf_8')
            else:
                self.value.value = value

        except TypeError as err:
            if not err.args:
                err.args = ('',)
            err.args = err.args + ('Wrong type: expected %s, but got %s' %
                                   (type(self.get()).__name__, type(value).__name__),)
            raise


class MQTT(Section):
    broker_ip = Option(str)
    broker_port = Option(int)


class TEST(Section):
    test_var = Option(str)


def load(file_paths):
    _parser = ConfigParser()
    _parser.read(file_paths)

    for section_name, section in list(globals().items()):
        if hasattr(section, '__base__'):
            if section.__base__ == Section:

                for option_name, option in list(section.__dict__.items()):
                    if isinstance(option, Option):
                        try:
                            if option.type == str:
                                option.value = Array('c', 1024)
                                option.value.value = bytes(_parser.get(
                                    section_name, option_name, fallback=option.fallback), 'utf_8')

                            if option.type == int:
                                option.value = Value('i', _parser.getint(
                                    section_name, option_name, fallback=option.fallback))

                            if option.type == float:
                                option.value = Value('d', _parser.getfloat(
                                    section_name, option_name, fallback=option.fallback))

                            if option.type == bool:
                                option.value = Value('b', _parser.getboolean(
                                    section_name, option_name, fallback=option.fallback))
                        except TypeError as err:
                            if not err.args:
                                err.args = ('',)
                            err.args = err.args + ('No valid config entry or fallback value - var: %s %s, type: %s' % (
                                section_name, option_name, option.type.__name__),)
                            raise


def save(file_path):
    _parser = ConfigParser()

    for section_name, section in list(globals().items()):
        if hasattr(section, '__base__'):
            if section.__base__ == Section:

                for option_name, option in list(section.__dict__.items()):
                    if isinstance(option, Option):

                        if not _parser.has_section(section_name):
                            _parser.add_section(section_name)
                        _parser.set(section_name, option_name, str(option.get()))

    with open(file_path, 'w') as configfile:
        _parser.write(configfile)
