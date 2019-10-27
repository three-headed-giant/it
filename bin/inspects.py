"""
A python based DSL for InspectorTiger's testing

Every inspect file starts with a module-level doc-string.
Continues with a dictionary that specify requirements for 
the tests below that. The tests must be under a context manager.

Supported managers;
    - positive (true-positive)
    - negative (false-negative)


An example;
    '''Foo bar baz.
       with multi line'''
    
    {'require_function': True} # execution of statements below 
    # context manager should happen inside of a individual function
    
    with positive:
        inspector.tiger.should.find.this()
    with negative:
        inspector.tiger.should.not.find.this()

"""
import argparse
import ast
from argparse import ArgumentParser
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, NewType

Handler = NewType("Handler", ast.AST)


class HandlerFlag(Enum):
    POSITIVE = 0
    NEGATIVE = 1


@dataclass
class InspectFile:
    """Represents metadata for a inspected file"""

    name: str
    path: Path
    documentation: str = ""
    configuration: Dict[str, Any] = field(default_factory=dict)
    inspection_handlers: Dict[HandlerFlag, Handler] = field(
        default_factory=dict
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


def runner(origin):
    files = InspectFileParser.discover(origin)


def main(argv=None):
    parser = argparse.ArgumentParser(description="inspect file runner")
    parser.add_argument("path", type=Path)
    configuration = parser.parse_args()
    return runner(configuration.path)


if __name__ == "__main__":
    import sys

    main(sys.argv[:1])
