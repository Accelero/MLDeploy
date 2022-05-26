from configparser import ConfigParser

_UNSET = object()

_sections = []

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
                

def load(file_paths):
    _parser = ConfigParser()
    _parser.read(file_paths)

    for section_name, section in _sections:

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


def save(file_path):
    _parser = ConfigParser()

    for section_name, section in _sections:

                for option_name, option in list(section.__dict__.items()):
                    if isinstance(option, Option):

                        if not _parser.has_section(section_name):
                            _parser.add_section(section_name)
                        _parser.set(section_name, option_name,
                                    str(option.get()))

    with open(file_path, 'w') as configfile:
        _parser.write(configfile)

def register_sections(sections):
    global _sections
    if isinstance(sections, (list, tuple)):
        for section in sections:
            if issubclass(section, Section):
                _sections.append((section.__name__, section))
    else:
        if issubclass(sections, Section):
                _sections.append((sections.__name__, sections))
