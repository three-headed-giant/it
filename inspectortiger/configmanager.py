from collections import defaultdict
from configparser import ConfigParser
from multiprocessing import cpu_count
from pathlib import Path

from inspectortiger.utils import Level

BUILTIN_CONFIG = Path(__file__).parent / "config.ini"
USER_CONFIG = Path("~/.inspector.rc").expanduser()


class ConfigManager:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(BUILTIN_CONFIG)
        if USER_CONFIG.exists():
            self.config.read(USER_CONFIG)
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
            return tuple(Level.__members__.keys())
        elif "any" in levels:
            return ()
        else:
            return tuple(levels)

    @property
    def workers(self):
        workers = self.defaults.get("workers", "max")
        if workers.isdigit():
            workers = int(workers)
        else:
            workers = cpu_count()
        return workers

    @property
    def ignore(self):
        if "ignore" in self.defaults:
            return tuple(
                ignore.upper() for ignore in self.defaults["ignore"].split(", ")
            )
        else:
            return ()
