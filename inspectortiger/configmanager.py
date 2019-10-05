import importlib
import json
import logging
from contextlib import suppress
from dataclasses import dataclass, field
from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Optional

USER_CONFIG = Path("~/.inspector.rc").expanduser()
logger = logging.getLogger("inspectortiger")


class PluginLoadError(Exception):
    pass


class _Plugin:
    def __init_subclass__(cls):
        cls._singletons = {}

    def __new__(cls, *args):
        if not cls._singletons.get(args):
            cls._singletons[args] = super().__new__(cls)
        return cls._singletons[args]


@dataclass(unsafe_hash=True)
class Plugin(_Plugin):
    plugin: str
    namespace: str
    static_name: Optional[str] = None

    @classmethod
    def from_simple(cls, simple):
        namespace, plugin = simple.rsplit(".", 1)
        return cls(plugin, namespace)

    @classmethod
    def from_config(cls, config):
        result = []
        for namespace, plugins in config.items():
            result.extend(cls(plugin, namespace) for plugin in plugins)
        return result

    def __str__(self):
        return self.plugin

    def __post_init__(self):
        if self.static_name is None:
            self.static_name = f"{self.namespace}.{self.plugin}"

    def load(self):
        try:
            plugin = importlib.import_module(self.static_name)
            logger.debug(
                "{self.plugin} from {self.namespace} successfully loaded."
            )
            for actionable in dir(plugin):
                actionable = getattr(plugin, actionable)
                with suppress(AttributeError):
                    actionable.plugin = self
        except ImportError:
            logger.error("Couldn't load {self.plugin} from {self.namespace}.")


@dataclass
class Blacklist:
    plugins: List[Plugin] = field(default_factory=list)
    codes: List[str] = field(default_factory=list)

    def __post_init__(self):
        plugins = self.plugins.copy()
        for n, plugin in enumerate(self.plugins):
            if isinstance(plugin, str):
                plugins.pop(n)
                plugins.insert(n, Plugin.from_simple(plugin))
        self.plugins = plugins


@dataclass
class Config:
    workers: int = cpu_count()
    annotate: bool = False
    fail_exit: bool = True
    load_core: bool = True
    logging_level: int = logging.INFO
    logging_handler_level: int = logging.INFO

    plugins: List[Plugin] = field(default_factory=list)
    blacklist: Blacklist = field(default_factory=Blacklist)

    def __post_init__(self):
        if isinstance(self.plugins, dict):
            self.plugins = Plugin.from_config(self.plugins)

        if isinstance(self.blacklist, dict):
            self.blacklist = Blacklist(**self.blacklist)


class ConfigManager:
    def __init__(self):
        self.config = Config(**self._parse_config(USER_CONFIG))

    @staticmethod
    def _parse_config(path):
        if not path.exists():
            logger.warning("Couldn't find configuration file at {path!r}.")
            return {}
        with open(path) as config:
            try:
                config = json.load(config)
            except json.JSONDecodeError:
                config = {}
        return config
