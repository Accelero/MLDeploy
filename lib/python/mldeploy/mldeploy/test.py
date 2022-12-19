import yaml
from datetime import datetime, timedelta

def override(base: dict, override_dict: dict):
    if not isinstance(base, dict) or not isinstance(override_dict, dict):
        raise TypeError('parameters must be of type dict')
    for k, v in override_dict.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            override_dict(base[k], v)
        else:
            base[k] = v
    return base

class Section():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict):
                self.__setattr__(k, Section(**v))
            else:
                self.__setattr__(k, Option(v))
        
    def __getitem__(self, item):
        return self.__getattribute__(item)


class Option():
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value
    
    def get_timedelta(self):
        pass


class Config():
    def __init__(self):
        self._dict = {}

    def load(self, *file_paths):
        for path in file_paths:
            data = yaml.load(open(path), yaml.BaseLoader)
            self._dict = override(self._dict, data)

        for k, v in self._dict.items():
            if isinstance(v, dict):
                self.__setattr__(k, Section(**v))
            else:
                self.__setattr__(k, Option(v))

    def __getitem__(self, item):
        return self.__getattribute__(item)


class OptionError(Exception):
    pass


if __name__ == '__main__':
    config = Config()
    config.load('data/test.yaml', 'data/abc.yaml')
    print(config['foo']['bar']['string_var'].get())
