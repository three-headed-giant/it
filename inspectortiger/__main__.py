import argparse
import ast
import tokenize
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from pprint import pprint

import inspectortiger.inspects
from inspectortiger.inspector import Inspector
from inspectortiger.utils import Level
from reportme.publisher import ReportBuffer
from reportme.reporter import Report


class DoesntExist(Exception):
    pass


def main():
    parser = argparse.ArgumentParser(description="InspectorTiger")
    parser.add_argument(
        "paths", metavar="p", type=Path, nargs="+", help="paths to check"
    )
    parser.add_argument(
        "-l", "--levels", type=str, nargs="*", help="whitelist of levels"
    )
    args = parser.parse_args()
    files = []

    try:
        levels = [
            getattr(Level, level.upper())
            for level in args.levels or Level.__members__.keys()
        ]
    except AttributeError as exc:
        raise DoesntExist(
            f"Specified level doesnt exist, it must be in this list: {', '.join(Level.__members__.keys())}"
        ) from exc

    for path in args.paths:
        if not path.exists():
            raise DoesntExist(path)

        if path.is_file():
            files.append(path)
        else:
            files.extend(path.glob("**/*.py"))

    results = defaultdict(list)
    for file in files:
        inspector = Inspector(file)
        with tokenize.open(file) as f:
            content = f.read()
        inspector.visit(ast.parse(content))
        for level, result in inspector.results.items():
            results[level].extend(result)

    results = {level: results[level] for level in levels if results[level]}
    with Report(name="InspectorTiger", version="1.0.0") as report:
        report.description = "Tiger inspected your code and find these mistakes"

        with report.add_category(name="Pythonicity") as pythonicity:
            for level in results:
                with pythonicity.add_node(level.name.title()) as approachs:
                    for approach in results[level]:
                        approachs.add_requirement(**asdict(approach))

    buf = ReportBuffer()
    buf.render(report)
    buf.print()


if __name__ == "__main__":
    main()
