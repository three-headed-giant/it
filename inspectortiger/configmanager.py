from collections import defaultdict
from configparser import ConfigParser
from pathlib import Path

from inspectortiger.utils import Level

BUILTIN_CONFIG = Path(__file__).parent / "config.ini"
CONFIG_DIRECTORY = Path("~/.inspector.rc").expanduser()


class ConfigManager:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(BUILTIN_CONFIG)
        if CONFIG_DIRECTORY.exists():
            self.config.read(CONFIG_DIRECTORY)
        self.defaults = self.config["Config inspectortiger"]

    def discover(self):
        plugins = defaultdict(dict)
        for section in self.config.sections():
            if section.startswith("Plugins "):
                namespace = section[len("Plugins ") :]
                plugins[namespace].update(self.config[section])
        return plugins

    @property
    def levels(self):
        if "levels" in self.defaults:
            levels = self.defaults["levels"].split(", ")
        else:
            levels = ["all"]

        if "all" in levels:
            return Level.__members__.keys()
        elif "any" in levels:
            return ()
        else:
            return levels

    @property
    def ignore(self):
        if "ignore" in self.defaults:
            return [ignore.upper() for ignore in self.defaults["ignore"].split(", ")]
        else:
            return ()
