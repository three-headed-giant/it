# InspectorTiger
![CI](https://github.com/thg-consulting/it/workflows/CI/badge.svg)
![codecov.io](http://codecov.io/github/thg-consulting/it/coverage.svg?branch=master)
![PyPI version](https://badge.fury.io/py/it.svg)
![black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)
![Dependency Free](https://img.shields.io/static/v1?label=dependicy&message=free&color=success)

IT, Inspector Tiger, is a modern python code review tool / framework. It comes
with bunch of pre-defined handlers which warns you about improvements and possible
bugs. Beside these handlers, you can write your own or use community ones.

```py
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Foo(SomeObjects):
    def bar(self, x=[], y: Union[int, None] = None):
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

        my_other_iterable = list(map(itemgetter(0), tokens))
        for a in range(len(my_other_iterable)):
            print(a, "=>", my_other_iterable[a])

```

Think about this piece of code, you see some bugs or improvements, don't you?
But what if there were hundreds of lines code in this form inside your big codebase.
How would you find these patterns? By writing regex queries? LOL, of course not.

```console
$ it example.py
[Inspector Tiger] INFO - InspectorTiger inspected 🔎 and found these problems;
[Inspector Tiger] INFO - 
[upgrade]
  - example.py:1:0     => ALPHABET_CONSTANT
  - example.py:5:27    => OPTIONAL
  - example.py:9:16    => SUPER_ARGS
  - example.py:17:22   => USE_COMPREHENSION
  - example.py:18:8    => YIELD_FROM
  - example.py:21:28   => MAP_USE_COMPREHENSION
  - example.py:22:8    => BUILTIN_ENUMERATE
[general]
  - example.py:5:4     => DEFAULT_MUTABLE_ARG
  - example.py:8:12    => CONTROL_FLOW_INSIDE_FINALLY
  - example.py:8:12    => UNREACHABLE_EXCEPT
```

## Tutorials
- [Inspecting python with Inspector Tiger](https://dev.to/btaskaya/inspecting-python-with-inspector-tiger-3hfb)

## API
Also Inspector Tiger comes with a builtin server (`it.server`) which offers a
basic REST API. If you want to try it without downloading, you can use our heroku instance.

```console
(.venv) [  6:02PM  ]  [  isidentical@x200  ]
$ curl -s https://inspector.herokuapp.com -d '{"source": "Union[MyType, None]"}' | jq
{
  "status": "success",
  "result": {
    "upgradeable": [
      {
        "code": "OPTIONAL",
        "column": 0,
        "lineno": 1,
        "filename": "<unknown>"
      }
    ]
  }
}
```
