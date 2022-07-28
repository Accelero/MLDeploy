import configparser
from pathlib import Path


config_path = Path(__file__).parent / 'config.ini'
config = configparser.ConfigParser()
config.read('app/config.ini')
