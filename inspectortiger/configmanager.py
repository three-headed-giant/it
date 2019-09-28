from collections import defaultdict
from configparser import ConfigParser
from distutils.util import strtobool
from multiprocessing import cpu_count
from pathlib import Path

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
    def workers(self):
        workers = self.defaults.get("workers", "max")
        if workers.isdigit():
            workers = int(workers)
        else:
            workers = cpu_count()
        return workers

    @property
    def ignore(self):
        ignore = self.defaults.get("ignore", ())
        if ignore:
            ignore = tuple(ignore.upper() for ignore in ignore.split(", "))

        return ignore

    @property
    def fail_exit(self):
        fail_exit = self.defaults.get("fail exit", "yes")
        return strtobool(fail_exit)
