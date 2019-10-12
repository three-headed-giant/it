from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict

from inspectortiger.config_manager import Plugin, logger
from inspectortiger.inspector import Inspector

CORE_PLUGINS = Plugin.from_config(
    {"inspectortiger.plugins": ["context", "parentize", "misc", "upgradeable"]}
)


def inspect(file):
    results = {}
    try:
        logger.debug("Inspecting {}...")
        inspector = Inspector(file)
        inspector.handle()
        results = inspector.results
    except SyntaxError:
        logger.exception(f"Couldn't parse {file}")
    return results


def inspector(files, workers, ignore, debug=False):
    all_reports = defaultdict(list)

    if debug:
        executor = map
    else:
        executor = ProcessPoolExecutor(workers).map

    for inspection in executor(inspect, set(files)):
        for plugin, reports in inspection.items():
            for report in reports:
                if report.code not in ignore:
                    all_reports[plugin].append(asdict(report))

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
