# Contributing
This is a contributing guideline for Inspector Tiger.

## Environment
- Python 3.8 or higher
- [Pre-commit](https://pre-commit.com/)
- A fork of [`InspectorTiger`](https://github.com/thg-consulting/inspectortiger)

### Clone repository
```
$ git clone git@github.com:<USERNAME>/inspectortiger.git
$ cd inspectortiger
```

### Setup python
```
$ python3.8 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements-dev.txt
```

### Be sure it is the latest
```
$ git remote add upstream git@github.com:thg-consulting/inspectortiger.git
$ git fetch upstream
$ git rebase upstream/master
```

### Install pre-commit hooks
```
$ pre-commit install
$ pre-commit install --hook-type prepare-commit-msg
```

## Code
> "A foolish consistency is the hobgoblin of little minds"

Try to follow PEP8 & PEP20 but don't hesitate about following a style that is presented in this project but not complies with PEP8. If you are adding a new handler and you aren't sure about which plugin it fits, open an issue before sending PR.

By the way, after adding a new feature or fixing a bug please report your change to `CHANGELOG.md` (if possible, link the github issue).

### Commit Messages

We use `prefix: a short desc` template for our commit messages. Prefixes;

| prefix            | desc                                                                   |
|-------------------|------------------------------------------------------------------------|
| docs              | docs or typos                                                          |
| tests             | testing                                                                |
| inspector         | project core, includes `Inspector`, `ConfigManager` and plugin loading |
| command-line      | command line, __main__                                                 |
| plugins           | builtin plugins                                                        |
| community-plugins | community plugins                                                      |
| scripts           | internal scripts that are used to generate files like error_codes.md   |
| misc              | other                                                                  |

### Styling
We use `black` & `isort` and a bunch of `pre-commit` hooks. You dont need to do anything, `pre-commit` handles all.

### Testing
Testing is performed with `pytest`.

## Contact
If you have any question; you can contact me through [telegram](https://twitter.com/t.me/isidentical), [twitter](https://twitter.com/isidentical) or [mail](mailto:isidentical@gmail.com)
