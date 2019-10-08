from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict

from inspectortiger.config_manager import Plugin
from inspectortiger.inspector import Inspector

CORE_PLUGINS = Plugin.from_config(
    {"inspectortiger.plugins": ["context", "parentize", "misc", "upgradeable"]}
)


def inspect(file):
    inspector = Inspector(file)
    inspector.handle()
    return inspector.results


def inspector(files, workers, ignore):
    all_reports = defaultdict(list)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for inspection in executor.map(inspect, set(files)):
            for plugin, reports in inspection.items():
                for report in reports:
                    if report.code in ignore:
                        continue
                    report = asdict(report)
                    all_reports[plugin].append(report)

    return all_reports


def load_plugins(manager, ignore=(), load_core=True):
    def loader(plugins):
        for plugin in plugins:
            if plugin in ignore:
                continue
            else:
                plugin.load()

    if load_core:
        loader(CORE_PLUGINS)

    loader(manager.config.plugins)
