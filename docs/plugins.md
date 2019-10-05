# Plugins
InspectorTiger plugins


## Context
Context management for AST

- `db['context']` => Current context
- `db['previous_contexts']` => Previous contexts
- `db['next_contexts']` => Next contexts
- `db['global_context']` => Global context
- `get_context(node, db)` => Infer context of given `node`

## Misc
Common gotchas


## Parentize
`parent` field to each node

- `parent_to(child, node)` => yields all parents of child until it reaches `node`

## Unreachable Except
Unreacable excepts

- `db['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value

## Upgradeable
Improvable (for 3.8+) syntaxes


### Unimport
`unimport` integration

- `db['unimport']` => A list of imports that are not used
