import argparse
import ast
import tokenize
from dataclasses import asdict
from pathlib import Path
from pprint import pprint

from inspectortiger.inspector import Inspector
from reportme.publisher import ReportBuffer
from reportme.reporter import Report


class DoesntExist(Exception):
    pass


def main():
    parser = argparse.ArgumentParser(description="InspectorTiger")
    parser.add_argument(
        "paths", metavar="P", type=Path, nargs="+", help="paths to check"
    )
    args = parser.parse_args()
    files = []
    for path in args.paths:
        if not path.exists():
            raise DoesntExist(path)

        if path.is_file():
            files.append(path)
        else:
            files.extend(path.glob("**/*.py"))

    results = []
    for file in files:
        inspector = Inspector(file)
        with tokenize.open(file) as f:
            content = f.read()
        inspector.visit(ast.parse(content))
        results.extend(inspector.results)

    with Report(name="InspectorTiger", version="1.0.0") as report:
        report.description = "Tiger inspected your code and find these mistakes"

        with report.add_category(name="Pythonicity") as pythonicity:
            with pythonicity.add_node("Approachs") as approachs:
                for approach in results:
                    approachs.add_requirement(**asdict(approach))

    buf = ReportBuffer()
    buf.render(report)
    buf.print()


if __name__ == "__main__":
    main()
