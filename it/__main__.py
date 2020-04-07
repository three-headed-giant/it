import argparse
import sys
from distutils.util import strtobool
from pathlib import Path

from it.plugin import Plugin
from it.reports import _prepare_result
from it.session import Session
from it.utils import logger, prepare_logger, traverse_paths


def prepare_parser(session):
    parser = argparse.ArgumentParser(description="InspectorTiger")
    parser.add_argument(
        "paths", metavar="p", type=Path, nargs="*", help="paths to check"
    )

    parser.add_argument(
        "--ignore-plugin",
        nargs="*",
        default=session.config.blacklist.plugins,
        type=Plugin.from_simple,
        help="plugins to ignore",
    )
    parser.add_argument(
        "--ignore-code",
        type=str,
        nargs="*",
        default=session.config.blacklist.codes,
        help="handlers to ignore",
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="number of worker processes",
        default=session.config.workers,
    )
    parser.add_argument(
        "--fail-exit",
        type=strtobool,
        help="on fail exit with error code",
        default=session.config.fail_exit,
    )
    parser.add_argument(
        "--load-core",
        help="load core plugins (`it.plugins`)",
        default=session.config.load_core,
    )
    parser.add_argument(
        "--logging-level",
        type=int,
        default=session.config.logging_level,
        help="logging level",
    )
    parser.add_argument(
        "--logging-handler-level",
        type=int,
        default=session.config.logging_handler_level,
        help="stdout handler level",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        default=False,
        help="dont use process pool executor",
    )
    parser.add_argument(
        "--show-plugins",
        action="store_true",
        default=False,
        help="print all active plugins before start",
    )
    return parser


def main():
    files = []
    session = Session()
    configuration = prepare_parser(session).parse_args()
    prepare_logger(
        configuration.logging_level, configuration.logging_handler_level
    )

    session.config.update(**vars(configuration))
    session.start()

    if configuration.show_plugins:
        logger.info(
            f"Active plugins: {', '.join(plugin.static_name for plugin in session.plugins if not plugin.inactive)}"
        )

    if configuration.paths:
        files = traverse_paths(configuration.paths)
        reports = session.bulk_inspection(*files)
        if reports:
            logger.info(
                "InspectorTiger inspected \N{right-pointing magnifying glass} "
                "and found these problems;"
            )
            logger.info("\n" + _prepare_result(reports))
            exit(int(session.config.fail_exit))
        else:
            logger.info(
                "InspectorTiger inspected \N{right-pointing magnifying glass} "
                "your code and it is perfect \N{white heavy check mark}"
            )
    else:
        logger.info("Nothing to do!")


if __name__ == "__main__":
    main()
