# InspectorTiger
![CI](https://github.com/thg-consulting/inspectortiger/workflows/CI/badge.svg)
![codecov.io](http://codecov.io/github/thg-consulting/inspectortiger/coverage.svg?branch=master)
![PyPI version](https://badge.fury.io/py/inspectortiger.svg)
![black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)
![Dependicy Free](https://img.shields.io/static/v1?label=dependicy&message=free&color=success)

InspectorTiger is a modern python code review tool / framework. It comes with bunch of pre-defined handlers which warns you about improvements and possible bugs. Beside these handlers, you can write your own or use community ones.

## Example
```py
MY_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
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

        my_iterable = list(token[0] for token in tokens)
        for a in my_iterable:
            yield a
    
        for a in range(len(MY_ALPHABET)):
            print(a, "=>", MY_ALPHABET[a])
```
Think about this piece of code, you see some bugs or improvements, don't you? But what if there were hundreds of lines code in this form inside your big codebase. How would you find these patterns? By writing regex queries? LOL, of course not.
```console
$ inspectortiger ../t.py
[Inspector Tiger] INFO - InspectorTiger inspected 🔎 and found these problems;
[Inspector Tiger] INFO - 
[misc]
  - ../t.py:2:4     => DEFAULT_MUTABLE_ARG
  - ../t.py:5:12    => CONTROL_FLOW_INSIDE_FINALLY
  - ../t.py:5:12    => UNREACHABLE_EXCEPT
[upgradeable]
  - ../t.py:2:29    => OPTIONAL
  - ../t.py:6:16    => SUPER_ARGS
  - ../t.py:14:22   => USE_COMPREHENSION
  - ../t.py:15:8    => YIELD_FROM
  - ../t.py:18:28   => ALPHABET_CONSTANT
  - ../t.py:19:8    => BUILTIN_ENUMERATE
```

Buutt, what if i want something more specific? Like what if i want to find all calls to `xyz` function with 2 arguments only inside of a class inside of a class, can you implement this feature? Nop, but you can.

```py
xyz()
xyz(1, 2)
def yyy():
    xyz()
    xyz(1, 2)

class PamPam:
    xyz(1, 2)

    class FooFoo:
        xyz(1, 2) # this one

def papa():
    class Papa:
        xyz(1, 2)
        class FoFo:
            xyz(1, 2) # this one
```

To write a handler, you'll need a python package. Let's create a `setup.py` (or `setup.cfg`);
```
from setuptools import setup, find_packages

setup(
    name="xyzintro",
    packages=find_packages()
)
```
This would work (just for tutorial). Then we need an actual package which would contain an `__init__.py` and as many modules as we want.
```
├── xyzintro
│   ├── handlers.py
│   └── __init__.py
```
The only module in that example is the module that contains our handler. Let's take a look to that.
```py
from inspectortiger import Inspector
```
`Inspector` is the base of all the things. It controls workflow by handlers etc.
```py
from inspectortiger.utils import name_check
```
`name_check` is a small utility that compares given `ast.Name`'s `id` attribute.
```py
from inspectortiger.plugins.context import Contexts
```
The `Contexts` is an `enum` which contain context states.


After import a decorator comes in,
```py
@Inspector.register(ast.Call)
```
Which registers our function (below that) to the `Inspector` with an AST node. When the `InspectorTiger` encounters with that node, it'll call our function.
```py
def xyzinspector(node, db):
    """Finds all `xyz()` calls with 2 arguments inside of 2-level-depth class context."""
```
The first thing we need to do is to find what the current context is and what the previous context was. If both of these are classes, we can proceed.
```py
    prev = db["context"]["previous_contexts"]
    depth_one = db["context"]["context"].context is Contexts.CLASS
    if len(prev) > 0:
        depth_two = prev[-1].context is Contexts.CLASS
    else:
        depth_two = False
```
Luckily Inspector Tiger has a core plugin for deciding our context, `inspectortiger.plugins.context`. First thing we did was accessing the hook database (`db`) which allows hooks to share data between them. Then we got our current context (`depth_one`). We performed a check because we could be in the global scope and if that's the case, `prev[-1]` will raise an error. After deciding the status of the our contexts,
```py
    return (
        depth_one
        and depth_two
        and name_check(node.func, "xyz")
        and len(node.args)== 2
    )
```
we are ready to return a value. If the value is `True`, `Inspector` will put this investigaton code to report. If it's `False`, then inspector will pass.


Last thing we need to do is to activate our plugin by creating/modifiying the `~/.inspector.rc` file;
```json
{
    ...
    "plugins": {
        "<package>": ["<modules>", "<that>", "<contains>", "<handlers>"],
        "xyzintro": ["handlers"]
    }
    ...
}

```
