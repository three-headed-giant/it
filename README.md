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

**Question**: How can i contribute?

**Answer**: We have a [contributing](https://github.com/thg-consulting/inspectortiger/blob/master/docs/contributing.md) file for the environment and some basics. After that is fixing bugs or adding handlers for patterns you regularly encounter with.

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

##

**Question**: How to configure `~/.inspect.rc`


**Answer**: Beside the plugin registrations, other settings is a part of `[Config inspectortiger]` section

| setting   | description                                      | type                                      | cmdline flag   |
|-----------|--------------------------------------------------|-------------------------------------------|----------------|
| ignore    | which handlers to ignore                         | name of the handlers seperated by a comma | --ignore       |
| workers   | child processes to spawn for parallel processing | an integer or 'max'                       | --workers      |
| fail exit | on fail exit with error code                     | yes/no/true/false etc.                    | --fail-exit    |


##

**Question**: Can i use this as an pre-commit hook?

**Answer**: Yes, just add this to your `.pre-commit-config.yml`

```yml
-   repo: https://github.com/thg-consulting/inspectortiger
    rev: master
    hooks:
    -   id: inspectortiger
```
