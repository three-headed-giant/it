import argparse
import tokenize
import ast
from pathlib import Path
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

    inspector = Inspector()
    for file in files:
        with tokenize.open(file) as f:
            content = f.read()
        inspector.visit(ast.parse(content))

    print(inspector.results)


if __name__ == "__main__":
    main()
