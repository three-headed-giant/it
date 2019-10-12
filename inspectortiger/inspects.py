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
        results = inspector.handle()
    except SyntaxError:
        logger.exception(f"Couldn't parse {file}")
    return results


def _obtain(ignore, *inspections):
    all_reports = defaultdict(list)

    for inspection in inspections:
        for plugin, reports in inspection.items():
            for report in reports:
                if report.code not in ignore:
                    all_reports[plugin].append(asdict(report))

    return all_reports


def inspector(files, workers, ignore, debug=False):
    if debug:
        executor = map
    else:
        executor = ProcessPoolExecutor(workers).map

    return _obtain(ignore, *executor(inspect, set(files)))


def _load_plugins(plugins, ignore=()):
    for plugin in plugins:
        if plugin in ignore:
            continue
        else:
            plugin.load()


def start_core_session(ignore=()):
    _load_plugins(CORE_PLUGINS, ignore)


def load_plugins(manager, ignore=(), load_core=True):
    if load_core:
        start_core_session(ignore)

    _load_plugins(manager.config.plugins, ignore)
