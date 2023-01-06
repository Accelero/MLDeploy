from pathlib import Path
import configparser
import os

# path to config file
pathToConfig = Path(__file__).parent / 'config.ini'

# path to config file with overrides when environment variable DEVMODE is set to 1
pathToConfigOverrides = Path('dev/configoverrides.ini')


class CustomConfig():
    def __init__(self, path):
        self.path = path
        self.parser = configparser.ConfigParser()
        self.read(path)
        self.update()

    def read(self, path):
        self.parser.read(path)

    def update(self):
        # Here are config variables assigned. Config variables can be accessed
        # in other modules by importing "config"
        # from this module and using config.<varname>.
        # The variable type is defined here, aswell as fallback values.
        self.window_width = self.parser.get('General', 'window_width', fallback='5s')
        self.window_step = self.parser.get('General', 'window_step', fallback='1s')
        self.influxdb_url = self.parser.get('Influxdb', 'url')
        self.influxdb_username = self.parser.get('Influxdb', 'username')
        self.influxdb_password = self.parser.get('Influxdb', 'password')
        self.influxdb_database_read = self.parser.get('Influxdb', 'database_read')
        self.influxdb_database_write = self.parser.get('Influxdb', 'database_write')



    def save(self):
        with open(self.path, 'w') as configfile:
            self.parser.write(configfile)

    def toDict(self):
        out = {}
        for s in self:
            d = {}
            for o in self[s]:
                d[o] = self.get(s, o)
            out[s] = d
        return out


config = CustomConfig(pathToConfig)

if os.environ.get('DEVMODE') == '1':
    config.read(pathToConfigOverrides)
    config.update()