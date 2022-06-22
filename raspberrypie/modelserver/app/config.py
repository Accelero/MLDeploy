from pathlib import Path
import configparser
import os

pathToConfig = Path(__file__).parent / 'config.ini'
pathToConfigOverrides = Path('dev/configoverrides.ini')

class ExtendedConfigParser(configparser.ConfigParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        super().read(path)
    
    def save(self):
        with open(self.path, 'w') as configfile:
            super().write(configfile)
    
    def toDict(self):
        out = {}
        for s in self:
            d = {}
            for o in self[s]:
                d[o] = self.get(s, o)
            out[s] = d
        return out


config = ExtendedConfigParser(pathToConfig)

if os.environ.get('DEVMODE') == '1':
    config.read(pathToConfigOverrides)