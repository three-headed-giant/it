# InspectorTiger
![CI](https://github.com/thg-consulting/inspectortiger/workflows/CI/badge.svg)
![codecov.io](http://codecov.io/github/thg-consulting/inspectortiger/coverage.svg?branch=master)
![PyPI version](https://badge.fury.io/py/inspectortiger.svg)
![black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Dependicy Free](https://img.shields.io/static/v1?label=dependicy&message=free&color=success)

InspectorTiger is a modern python code review tool which warns you about improvable code and possible bugs. For an example if you have a function where you assing an argument's default value to a mutable object (like list) it'll warn you.


## FAQ

**Question**: Where does the Inspector Tiger name come from?


**Answer**: It is a [character](https://montypython.fandom.com/wiki/Inspector_Tiger) from Monty Python

##

**Question**: How does InspectorTiger works?


**Answer**: It analyzes python code by converting it to an [abstract syntax tree](https://docs.python.org/3/library/ast.html). Then it visits tree top to bottom. On every visit, it'll invoke the registered plugins to that node.

##

**Question**: So, it is a plugin based tool?


**Answer**: Yes, it is. Every handler in InspectorTiger is a plugin. There are 3 kinds of plugins:

| type      | active   | aim                                      |
|-----------|----------|------------------------------------------|
| builtins  | yes      | finds improvable code                    |
| community | no       | allows integration of other python tools |
| user      | no       | for inspecting project-specific pieces   |

##

**Question**: How does plugin system works?


**Answer**: Plugins are simply python packages and they are configured in `~/.inspector.rc`. On every run, InspectorTiger will read your configuration and try to register plugins you've specified.


An example plugin which checks if a function name starts with dunder.
```py
# example_plugins/example_plugin.py

from inspectortiger import Inspector
from inspectortiger.utils import Level

```
```py
@Inspector.register(ast.FunctionDef)
```
This is a registration to a specific node, this function will be invoked when a `FunctionDef` node comes.

```py
@Level.HIGH
```
Level defines severity of this event. It allows users to ignore / allow only needed plugins.
```py
def name_startswith_underscore(node, db):
    return node.name.startswith("__")
```
The function takes the node itself and a database which can contain some useful information about file.


When this package installed, then `~/.inspect.rc` should be configured to activate this plugin.
```ini
[Plugins example_plugins]
```
This section specifies all plugins that are defined in here is a part of `example_plugins` package.

```
check name dunder = example_plugin
```
`check name dunder` is the name of our plugin, and the `example_plugin` is the module which is located inside of `example_plugins`

##

**Question**: How to configure `~/.inspect.rc`


**Answer**: Beside the plugin registrations, other settings is a part of `[Config inspectortiger]` section

| setting   | description                                      | type                                                               |
|-----------|--------------------------------------------------|--------------------------------------------------------------------|
| levels    | which levels to allow                            | level names seperated by a comma or all/any                        |
| ignore    | which plugins to ignore                          | name of the plugins seperated by a comma (e.g default_mutable_arg) |
| workers   | child processes to spawn for parallel processing | an integer or 'max'                                                |

##

**Question**: What are the severity levels?


**Answer**: Severity levels shows how important that handler's check is. There are currently 6 levels: EXTREME_LOW, LOW, AVG, HIGH, EXTREME_HIGH

##

**Question**: Can i use this as an pre-commit hook?

**Answer**: Yes, just add this to your `.pre-commit-config.yml`

```yml
-   repo: https://github.com/thg-consulting/inspectortiger
    rev: master
    hooks:
    -   id: inspectortiger
```
