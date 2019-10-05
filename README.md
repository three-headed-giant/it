# InspectorTiger
![CI](https://github.com/thg-consulting/inspectortiger/workflows/CI/badge.svg)
![codecov.io](http://codecov.io/github/thg-consulting/inspectortiger/coverage.svg?branch=master)
![PyPI version](https://badge.fury.io/py/inspectortiger.svg)
![black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Dependicy Free](https://img.shields.io/static/v1?label=dependicy&message=free&color=success)

InspectorTiger is a modern python code review tool / framework. It comes with bunch of pre-defined handlers which warns you about improvable code and possible bugs. Beside that handlers you can write your handler or use community handlers.

## Example
```py
class Foo(SomeObjects):
    def bar(self, x = [], y: Union[int, None] = None):
        x.append(1)
        for _ in range(3):
            try:
                super(bla, bla).foo_baz()
            except Exception:
                print("An exception")
            except AttributeError:
                print("An attribute error")
            finally:
                continue

        for a in x:
            yield a
```
Think about this piece of code, you see some bugs or improvable code don't you? But what if there are hundreds of lines code in this form inside your big codebase. How can you find that patterns? By writing regex queries? LOL, of course not.
```json
$ python -m inspectortiger my_big_codebase/ # P.S: stripped file name information
{
    "misc": [
        {
            "code": "DEFAULT_MUTABLE_ARG",
            "lineno": 2,
        },
        {
            "code": "CONTROL_FLOW_INSIDE_FINALLY",
            "lineno": 5,
        }
    ],
    "upgradeable": [
        {
            "code": "OPTIONAL",
            "lineno": 2,
        },
        {
            "code": "SUPER_ARGS",
            "lineno": 6,
        },
        {
            "code": "YIELD_FROM",
            "lineno": 14,
        }
    ],
    "unreachable_except": [
        {
            "code": "UNREACHABLE_EXCEPT",
            "lineno": 5,
        }
    ]
}
```
