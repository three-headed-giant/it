"""A python based DSL for InspectorTiger's testing."""

import argparse
import ast
import random
import string
import textwrap
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import chain
from pathlib import Path
from typing import Any, Dict, List, NewType

import inspectortiger.plugins
from inspectortiger.inspector import Inspector
from inspectortiger.session import Session
from inspectortiger.utils import Group

try:
    import astor
except ImportError:
    HAS_ASTOR = False

    def get_source(node):
        print(
            ">>> Please install astor to see source code"
        )  # TODO: refactor with ast.get_source_segment


else:
    HAS_ASTOR = True

    def get_source(node):
        source = astor.to_source(node)
        source = "\n".join(line for line in source.split("\n") if line)
        return source


AVG = 24
AVG_RESULT = 40
BASE = Path(inspectortiger.plugins.__file__).parent
DEFAULT_CONFIG = {"require_function": True}

Handler = NewType("Handler", ast.AST)


class HandlerFlag(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()

    def verify_result(self, inspection, result):
        runner = getattr(self, f"_{self.name.lower()}_verifier")
        return runner(inspection, result)

    def _positive_verifier(self, inspection, result):
        return len(result) == 1 and inspection.name.upper() in result

    def _negative_verifier(self, inspection, result):
        return len(result) == 0


@dataclass
class Result:
    """Result of a test run"""

    flag: HandlerFlag
    result: bool
    test_case: Handler


@dataclass
class InspectFile:
    """Represents metadata for a inspected file"""

    name: str
    path: Path
    documentation: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    inspection_handlers: Dict[HandlerFlag, List[Handler]] = field(
        default_factory=lambda: defaultdict(list)
    )


class InspectFileParser(ast.NodeVisitor):
    """Queries relevant metadata from files with searching constants"""

    def __init__(self, filename):
        self.result = InspectFile(filename.stem, filename)

    @classmethod
    def discover(cls, origin):
        """Recursively searches all `inspect` files and starts a
        new InspectFileParser instances whenever it encounters with 
        one.
        """

        results = []
        for inspect_file in origin.glob("**/*.inspect"):
            parser = cls(inspect_file)
            parser.visit(ast.parse(inspect_file.read_text()))
            if not parser.result.configuration:
                parser.result.configuration = DEFAULT_CONFIG.copy()
            results.append(parser.result)
        return results

    def visit_Constant(self, node):
        if isinstance(node.value, str) and self.result.documentation == "":
            self.result.documentation = node.value
        else:
            self.generic_visit(node)

    def visit_Dict(self, node):
        if self.result.configuration:
            self.generic_visit(node)
        else:
            self.result.configuration = ast.literal_eval(node)

    def visit_With(self, node):
        flag = HandlerFlag[node.items[0].context_expr.id.upper()]
        self.result.inspection_handlers[flag].append(node.body)


def _name_faker():
    test_id = "".join(random.sample(string.ascii_letters, 8))
    return "__inspection_test_" + test_id


def prepare_function(body):
    function = ast.FunctionDef(
        name=_name_faker(),
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=body,
        decorator_list=[],
    )
    ast.fix_missing_locations(function)
    return function


def prepare_module(body):
    module = ast.Module(body=body)
    ast.fix_missing_locations(module)
    return module


def group_cases(cases, config):
    if config.get("require_function"):
        cases = [prepare_function(case) for case in cases]
    if config.get("require_module"):
        cases = [prepare_module(case) for case in cases]
    return cases


def print_fails_verbose(session, fails):
    for result in fails:
        print("FAIL ==>")
        print(f"    Flag: {result.flag}")
        print(
            f"    Result: {dict(session.single_inspection(result.test_case))}"
        )
        print(textwrap.indent(get_source(result.test_case), " " * 4), "\n")


def runner(origin, show_errors=False):
    session = Session()
    session.config.update(load_core=True, plugins={})

    session.start()
    available_handlers = chain.from_iterable(Inspector._hooks.values())
    available_handlers = {
        handler.__name__: handler for handler in available_handlers
    }

    results = defaultdict(list)
    inspections = InspectFileParser.discover(origin)
    print(f"Collected {len(inspections)} inspections...")
    for inspection in inspections:
        if inspection.name not in available_handlers:
            print(
                f"Skipping unknown plugin: {inspection.name} (from {inspection.path!s})"
            )
            continue

        for flag, test_cases in inspection.inspection_handlers.items():
            test_cases = tuple(chain.from_iterable(test_cases))
            inspection.inspection_handlers[
                flag
            ] = new_test_cases = group_cases(
                test_cases, inspection.configuration
            )

            for index, test_case in enumerate(new_test_cases):
                result = session.single_inspection(test_case, strict=True)
                result = dict(session.group_by(result, Group.CODE))
                result = flag.verify_result(inspection, result)
                results[inspection.name].append(
                    Result(flag, result, test_cases[index])
                )

    fail = False
    for test, results in results.items():
        fails = []
        padding = AVG_RESULT - len(results)

        print(test, " =>> ", end=" ", sep=abs(AVG - len(test)) * " ")

        for result in results:
            if not result.result:
                fails.append(result)
            print(str(result.result)[0], end="")

        if fails:
            fail = True
            print(padding * " ", "[FAILED]")
            if show_errors:
                print_fails_verbose(session, fails)
        else:
            print(padding * " ", "[SUCCEED]", sep="")

    exit(bool(fails))


def main(argv=None):
    parser = argparse.ArgumentParser(description="inspect file runner")
    parser.add_argument("origin", type=Path)
    parser.add_argument("--show-errors", action="store_true", default=False)
    configuration = parser.parse_args()
    return runner(**vars(configuration))


if __name__ == "__main__":
    import sys

    main(sys.argv[:1])
