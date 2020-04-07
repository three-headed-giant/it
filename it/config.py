import json
import logging
from dataclasses import dataclass, field
from multiprocessing import cpu_count
from typing import List

from it.plugin import Plugin


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

    def extend(self, other):
        self.plugins.extend(other.plugins)
        self.codes.extend(other.codes)


@dataclass
class Config:
    serial: bool = False
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

    def read(self, path):
        return self.update(self._parse_config(path))

    def update(self, **fields):
        pre_config = self.__class__(**self.reconstruct_fields(fields))
        for attribute, value in vars(pre_config).items():
            if isinstance(value, (Blacklist, list)):
                current = getattr(self, attribute)
                current.extend(value)
            else:
                setattr(self, attribute, value)

    def reconstruct_fields(self, fields):
        return {
            attr: val for attr, val in fields.items() if hasattr(self, attr)
        }

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
