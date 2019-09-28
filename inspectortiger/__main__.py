import argparse
import ast
import json
import tokenize
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from distutils.util import strtobool
from pathlib import Path

from inspectortiger.configmanager import ConfigManager
from inspectortiger.inspector import Inspector
from inspectortiger.inspects import load_plugins


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
    parser.add_argument("--plugins", type=str, nargs="*", help="whitelist of plugins")
    parser.add_argument(
        "--ignore",
        type=str,
        nargs="*",
        default=manager.ignore,
        help="handlers to ignore",
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="number of worker processes",
        default=manager.workers,
    )
    parser.add_argument(
        "--fail-exit",
        type=strtobool,
        help="on fail exit with error code",
        default=manager.fail_exit,
    )
    args = parser.parse_args()
    load_plugins(manager, args.plugins)

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
            for plugin, reports in inspection.items():
                all_reports[plugin].extend(
                    asdict(report)
                    for report in reports
                    if report.code not in args.ignore
                )

    if all_reports:
        print(
            "InspectorTiger inspected \N{right-pointing magnifying glass}"
            "and found these problems;"
        )
        print(json.dumps(all_reports, indent=4))
        if args.fail_exit:
            exit(1)
    else:
        print(
            "InspectorTiger inspected \N{right-pointing magnifying glass}"
            "your code and it is perfect \N{white heavy check mark}"
        )


if __name__ == "__main__":
    main()
