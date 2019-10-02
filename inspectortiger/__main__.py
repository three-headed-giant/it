import argparse
import json
from distutils.util import strtobool
from pathlib import Path

from inspectortiger.configmanager import ConfigManager
from inspectortiger.inspects import inspector, load_plugins


def traverse_paths(paths):
    files = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)

        if path.is_file():
            files.append(path)
        else:
            files.extend(path.glob("**/*.py"))
    return files


def main():
    files = []
    manager = ConfigManager()

    parser = argparse.ArgumentParser(description="InspectorTiger")

    parser.add_argument(
        "paths", metavar="p", type=Path, nargs="*", help="paths to check"
    )

    parser.add_argument(
        "--annotate",
        default=False,
        action="store_true",
        help="include code to reports",
    )
    parser.add_argument(
        "--ignore-plugin", type=str, nargs="*", help="plugins to ignore"
    )
    parser.add_argument(
        "--ignore-code",
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
    load_plugins(manager, args.ignore_plugin)

    if args.paths:
        files = traverse_paths(args.paths)
        reports = inspector(
            files, args.workers, args.ignore_code, args.annotate
        )
        if reports:
            print(
                "InspectorTiger inspected \N{right-pointing magnifying glass} "
                "and found these problems;"
            )
            print(json.dumps(reports, indent=4))
            if args.fail_exit:
                exit(1)
        else:
            print(
                "InspectorTiger inspected \N{right-pointing magnifying glass} "
                "your code and it is perfect \N{white heavy check mark}"
            )
    else:
        print("Nothing to do!")


if __name__ == "__main__":
    main()
