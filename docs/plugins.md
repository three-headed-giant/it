# Plugins
InspectorTiger plugins


## Context
Context management for AST

- `db['context']` => Current context
- `db['previous_contexts']` => Previous contexts
- `db['next_contexts']` => Next contexts
- `db['global_context']` => Global context
- `get_context(node, db)` => Infer context of given `node`

## Unreachable Except
Unreacable excepts

- `db['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value

## Upgradeable
Improvable (for 3.8+) syntaxes


## Misc
Common gotchas


### Unimport
`unimport` integration

- `db['unimport']` => A list of imports that are not used
