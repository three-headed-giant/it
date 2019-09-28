#!/usr/bin/env python
import argparse
from importlib import import_module
from pathlib import Path

import inspectortiger.plugins

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

    with open(args.output, "w") as out:
        out.write("# Plugins\n")
        out.write("InspectorTiger plugins\n\n")
        for plugin in plugins:
            if plugin.__doc__:
                out.write(plugin.__doc__)


if __name__ == "__main__":
    generate()
