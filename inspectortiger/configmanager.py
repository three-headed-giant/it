import importlib
from collections import defaultdict
from configparser import ConfigParser
from pathlib import Path

BUILTIN_CONFIG = Path(__file__).parent / "config.ini"


class ConfigManager:
    def __init__(self, config_path=None):
        self.config = ConfigParser()
        if config_path:
            self.config.read(config_path)
        self.config.read(BUILTIN_CONFIG)

    def discover(self):
        plugins = defaultdict(dict)
        for section in self.config.keys():
            if section.startswith("Plugins "):
                namespace = section[len("Plugins ") :]
                plugins[namespace].update(self.config[section])
        return plugins
