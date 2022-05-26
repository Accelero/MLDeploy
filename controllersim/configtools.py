from configparser import ConfigParser
import inspect
import sys

_UNSET = object()


class Section():
    pass


class Option():
    def __init__(self, type, fallback=_UNSET):
        self.type = type
        self.fallback = fallback
        self.value = None

    def get(self):
        return self.value

    def set(self, value):
        if isinstance(value, self.type) or isinstance(value, type(None)):
            self.value = value
        elif value == _UNSET:
            raise TypeError(
                'Assignment failed, wrong type: expected %s or None, but got no config entry and no fallback' % self.type.__name__)
        else:
            raise TypeError('Assignment failed, wrong type: expected %s or None, but got %s' % (
                self.type.__name__, type(value).__name__))

class ConfigManager():
    def __init__(self):
        frame_infos = inspect.stack()
        for frame_info in frame_infos:
            module = inspect.getmodule(frame_info.frame)
            if module and module is not sys.modules[__name__]:
                self.module = module
                break

    def get_sections(self):
        sections = []
        for item in self.module.__dict__.values():
            if inspect.isclass(item):
                if item.__base__ == Section:
                    sections.append(item)
        return sections

    def load(self, file_paths):
        _parser = ConfigParser()
        _parser.read(file_paths)
        sections = self.get_sections()

        for section in sections:
            section_name = section.__name__
            for option_name, option in list(section.__dict__.items()):
                if isinstance(option, Option):

                    try:
                        if option.type == str:
                            option.set(_parser.get(
                                section_name, option_name, fallback=option.fallback))

                        if option.type == int:
                            option.set(_parser.getint(
                                section_name, option_name, fallback=option.fallback))

                        if option.type == float:
                            option.set(_parser.getfloat(
                                section_name, option_name, fallback=option.fallback))

                        if option.type == bool:
                            option.set(_parser.getboolean(
                                section_name, option_name, fallback=option.fallback))
                    except TypeError as err:
                        if not err.args:
                            err.args = ('',)
                        err.args = err.args + ('No valid config entry or fallback - var: %s %s, type: %s' % (
                            section_name, option_name, option.type.__name__),)
                        raise

    def save(self, file_path):
        _parser = ConfigParser()
        sections = self.get_sections()

        for section in sections:
            section_name = section.__name__
            for option_name, option in list(section.__dict__.items()):
                if isinstance(option, Option):

                    if not _parser.has_section(section_name):
                        _parser.add_section(section_name)
                    _parser.set(section_name, option_name,
                                str(option.get()))

        with open(file_path, 'w') as configfile:
            _parser.write(configfile)

