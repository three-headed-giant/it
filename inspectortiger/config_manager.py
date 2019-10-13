import importlib
import json
import logging
import sys
from dataclasses import dataclass, field
from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Optional, Tuple

import inspectortiger.inspector
from inspectortiger.utils import _PSEUDO_FIELDS

USER_CONFIG = Path("~/.inspector.rc").expanduser()
PROJECT_CONFIG = Path(".inspector.rc")
logger = logging.getLogger("inspectortiger")


class PluginLoadError(ImportError):
    pass


class _Plugin(type):
    _plugins = {}

    def __call__(
        cls,
        plugin,
        namespace,
        inactive=False,
        static_name=None,
        python_version=(),
    ):
        args = tuple(
            (k, v) for k, v in locals().items() if k not in _PSEUDO_FIELDS
        )
        if args not in cls._plugins:
            cls._plugins[args] = super().__call__(**dict(args))
        return cls._plugins[args]


@dataclass(unsafe_hash=True)
class Plugin(metaclass=_Plugin):
    plugin: str
    namespace: str
    inactive: bool = False
    static_name: Optional[str] = None
    python_version: Tuple[int, ...] = ()

    @classmethod
    def from_simple(cls, simple):
        try:
            namespace, plugin = simple.rsplit(".", 1)
        except ValueError:
            namespace, *plugin = simple

        plugin = "".join(plugin)
        return cls(plugin, namespace)

    @classmethod
    def from_config(cls, config):
        result = []
        for namespace, plugins in config.items():
            result.extend(
                cls.from_simple(f"{namespace}.{plugin}") for plugin in plugins
            )
        return result

    @classmethod
    def require(cls, plugin, namespace=None):
        def wrapper(func):
            if namespace is None:
                requirement = cls.from_simple(plugin)
            else:
                requirement = cls(plugin, namespace)

            if not hasattr(func, "requires"):
                func.requires = []
            func.requires.append(requirement)
            return func

        return wrapper

    def __post_init__(self):

        nsx = self.expand(self.namespace)
        self.namespace = nsx[:-1]

        if self.static_name is None:
            self.static_name = f"{nsx}{self.plugin}"

    def __str__(self):
        return self.plugin

    def load(self):
        with inspectortiger.inspector.Inspector.buffer():
            try:
                plugin = importlib.import_module(self.static_name)
            except ImportError:
                raise PluginLoadError(
                    f"Couldn't load '{self.plugin}' from `{self.namespace}` namespace!"
                )

            if hasattr(plugin, "__py_version__"):
                self.python_version = plugin.__py_version__

            if self.python_version > sys.version_info:
                self.inactive = True
                logger.debug(
                    f"`{self.plugin}` plugin from `{self.namespace}` couldn't load because of incompatible version."
                )
                raise inspectortiger.inspector.BufferExit

        for actionable in dir(plugin):
            actionable = getattr(plugin, actionable)
            if hasattr(
                actionable, "_inspection_mark"
            ):  # TODO: ismarked(callable)
                actionable.plugin = self

    @staticmethod
    def expand(namespace):
        # prefixes
        # @ => inspectortiger.plugins
        # ? => local plugin

        if namespace == "@":
            namespace = "inspectortiger.plugins"
        elif namespace.startswith("@"):
            namespace = namespace.replace("@", "inspectortiger.plugins.")
        elif namespace == "?":
            return ""

        return namespace + "."


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
        cfg = self._parse_config(USER_CONFIG)
        cfg.update(self._parse_config(PROJECT_CONFIG))
        self.config = Config(**cfg)

    @staticmethod
    def _parse_config(path):
        if not path.exists():
            logger.debug(f"Couldn't find configuration file at {path!s}.")
            return {}
        with open(path) as config:
            try:
                config = json.load(config)
            except json.JSONDecodeError:
                config = {}
        return config
