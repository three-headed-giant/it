import argparse
import ast
import tokenize
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

from inspectortiger.configmanager import ConfigManager
from inspectortiger.inspector import Inspector
from inspectortiger.inspects import load_plugins
from inspectortiger.reports import prepare
from inspectortiger.utils import PSEUDO_LEVELS, Level


def inspect(file):
    inspector = Inspector(file)
    with tokenize.open(file) as f:
        content = f.read()
    inspector.visit(ast.parse(content))
    return inspector.results


def main():
    files = []
    manager = ConfigManager()

    parser = argparse.ArgumentParser(description="InspectorTiger")
    parser.add_argument(
        "paths", metavar="p", type=Path, nargs="+", help="paths to check"
    )
    parser.add_argument(
        "-l", "--levels", type=str, nargs="*", help="whitelist of levels"
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="number of worker processes",
        default=manager.workers,
    )
    args = parser.parse_args()

    load_plugins(manager)
    try:
        levels = [
            getattr(Level, level.upper()) for level in args.levels or manager.levels
        ]
    except AttributeError as exc:
        raise ValueError(
            f"Specified level doesnt exist, it must be in this list: {', '.join(Level.__members__.keys())}"
        ) from exc

    levels = filter(lambda level: level not in PSEUDO_LEVELS, levels)

    for path in args.paths:
        if not path.exists():
            raise FileNotFoundError(path)

        if path.is_file():
            files.append(path)
        else:
            files.extend(path.glob("**/*.py"))

    all_reports = defaultdict(list)
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for inspection in executor.map(inspect, set(files)):
            for level, reports in inspection.items():
                report = filter(
                    lambda report: report.code not in manager.ignore, reports
                )
                all_reports[level].extend(reports)

    result = prepare(all_reports, levels)
    print(result)


if __name__ == "__main__":
    main()
