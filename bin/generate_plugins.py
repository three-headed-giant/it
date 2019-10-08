#!/usr/bin/env python
import argparse
from importlib import import_module
from itertools import chain
from pathlib import Path
from textwrap import dedent

import inspectortiger.plugins
from inspectortiger import Inspector

BASE = Path(inspectortiger.plugins.__file__).parent


def generate():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="output file")
    args = parser.parse_args()

    plugins = []
    for plugin in BASE.glob("**/*.py"):
        if plugin.parts[-1] == "__init__.py":
            continue

        plugin = plugin.relative_to(BASE)
        plugin = str(plugin)[: -len(plugin.suffix)].replace("/", ".")
        plugin = import_module(f"inspectortiger.plugins.{plugin}")
        plugins.append(plugin)

    with open(args.output / "plugins.md", "w") as out:
        out.write("# Plugins\n")
        out.write("InspectorTiger plugins\n\n")
        for plugin in plugins:
            if plugin.__doc__:
                out.write(plugin.__doc__)

    with open(args.output / "error_codes.md", "w") as out:
        out.write("# Error codes\n\n")
        handled = set()
        handlers = chain.from_iterable(Inspector._hooks.values())
        for handler in handlers:
            if handler.__name__ not in handled and handler.__doc__:
                handled.add(handler.__name__)

                parts = handler.__doc__.split("\n")
                state = False
                for n, part in enumerate(parts.copy()):
                    if "```" in part:
                        state = True
                    if state:
                        parts.pop(n)
                        parts.insert(n, part[4:])
                    if "py" not in part:
                        state = False

                result = "\n".join(parts)
                out.write(f"### {handler.__name__.upper()}\n")
                out.write(f"{result}\n")


if __name__ == "__main__":
    generate()
