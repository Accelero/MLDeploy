from configtools import *
import inspect


class MQTT(Section):
    broker_ip = Option(str)
    broker_port = Option(int)


class TEST(Section):
    test_var = Option(str)


sections = []
for name, item in list(globals().items()):
    if hasattr(item, '__base__'):
        if inspect.isclass(item):
            if issubclass(item, Section):
                sections.append(item)

register_sections(sections)