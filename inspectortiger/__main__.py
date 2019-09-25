import argparse
import ast
import tokenize
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

from reportme.publisher import ReportBuffer
from reportme.reporter import Report

from inspectortiger.configmanager import ConfigManager
from inspectortiger.inspector import Inspector
from inspectortiger.inspects import load_plugins
from inspectortiger.utils import PSEUDO_LEVELS, Level

parser = argparse.ArgumentParser(description="InspectorTiger")
parser.add_argument("paths", metavar="p", type=Path, nargs="+", help="paths to check")
parser.add_argument("-l", "--levels", type=str, nargs="*", help="whitelist of levels")
parser.add_argument("--workers", type=int, help="number of worker processes", default=4)


def inspect(file):
    inspector = Inspector(file)
    with tokenize.open(file) as f:
        content = f.read()
    inspector.visit(ast.parse(content))
    return inspector.results


def main(args):
    files = []
    manager = ConfigManager()
    load_plugins(manager)

    try:
        levels = [
            getattr(Level, level.upper()) for level in args.levels or manager.levels
        ]
    except AttributeError as exc:
        raise DoesntExist(
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

    results = defaultdict(list)
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for inspection in executor.map(inspect, set(files)):
            for level, result in inspection.items():
                result = filter(
                    lambda result: result.report.requirement not in manager.ignore,
                    result,
                )
                results[level].extend(result)

    results = {level: results[level] for level in levels if results[level]}
    with Report(name="InspectorTiger", version="1.0.0") as report:
        report.description = "Tiger inspected your code and found these mistakes"

        with report.add_category(name="Pythonicity") as pythonicity:
            for level in results:
                with pythonicity.add_node(level.name.title()) as approachs:
                    for approach in results[level]:
                        approachs.add_requirement(**asdict(approach))

    if results:
        buf = ReportBuffer()
        buf.render(report)
        buf.print()
        exit(1)
    else:
        print("Inspector tiger inspected your code and found it very well")


if __name__ == "__main__":
    main(parser.parse_args())
