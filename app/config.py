import configparser
from pathlib import Path
import configparser
import json
from typing import OrderedDict

pathToConfig = Path(__file__).parent / 'config.ini'
# config = configparser.ConfigParser()
# config.read(pathToConfig)

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

# def setWriteCfg(section, option, value):
#     config.set(section, option, value)
#     with open(pathToConfig, 'w') as configfile:
#         config.write(configfile)


# configDict = {}

# def convType(config, section, key, prefix):
#     if prefix == 'b': return config[section].getboolean(key)
#     if prefix == 'i': return config[section].getint(key)
#     if prefix == 'f': return config[section].getfloat(key)
#     if prefix == 's': return config[section][key]
#     raise ValueError('unhandled var type')
    

# def readConfig():
#     config.read(pathToConfig)
#     for s in config:
#         for k in config[s]:
#             splitk = k.split('_', 1)
#             configDict[splitk[1]] = convType(config, s, k, splitk[0])

# def writeConfig():
#     for k in configDict
#     config.write(pathToConfig)
