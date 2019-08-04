import argparse
import ast
import tokenize
from pathlib import Path
from pprint import pprint

from inspectortiger.inspector import Inspector


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

    pprint(results)


if __name__ == "__main__":
    main()
