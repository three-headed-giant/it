import argparse
import logging
import sys
from distutils.util import strtobool
from pathlib import Path

from inspectortiger.config_manager import ConfigManager, Plugin, logger
from inspectortiger.inspects import inspector, load_plugins
from inspectortiger.reports import _prepare_result


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
        "--ignore-plugin",
        nargs="*",
        default=manager.config.blacklist.plugins,
        type=Plugin.from_simple,
        help="plugins to ignore",
    )
    parser.add_argument(
        "--ignore-code",
        type=str,
        nargs="*",
        default=manager.config.blacklist.codes,
        help="handlers to ignore",
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="number of worker processes",
        default=manager.config.workers,
    )
    parser.add_argument(
        "--fail-exit",
        type=strtobool,
        help="on fail exit with error code",
        default=manager.config.fail_exit,
    )
    parser.add_argument(
        "--load-core",
        help="load core plugins (`inspectortiger.plugins`)",
        default=manager.config.load_core,
    )
    parser.add_argument(
        "--logging-level",
        type=int,
        default=manager.config.logging_level,
        help="logging level",
    )
    parser.add_argument(
        "--logging-handler-level",
        type=int,
        default=manager.config.logging_handler_level,
        help="stdout handler level",
    )

    args = parser.parse_args()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(args.logging_handler_level)
    logger.setLevel(args.logging_level)

    formatter = logging.Formatter(
        "[Inspector Tiger] %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    args = parser.parse_args()
    load_plugins(manager, args.ignore_plugin, args.load_core)

    if args.paths:
        files = traverse_paths(args.paths)
        reports = inspector(files, args.workers, args.ignore_code)
        if reports:
            logger.info(
                "InspectorTiger inspected \N{right-pointing magnifying glass} "
                "and found these problems;"
            )
            logger.info("\n" + _prepare_result(reports))
            if args.fail_exit:
                exit(1)
        else:
            logger.info(
                "InspectorTiger inspected \N{right-pointing magnifying glass} "
                "your code and it is perfect \N{white heavy check mark}"
            )
    else:
        print("Nothing to do!")


if __name__ == "__main__":
    main()
