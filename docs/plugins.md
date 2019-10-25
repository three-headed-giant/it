# Plugins
InspectorTiger plugins


## Context
Context management for AST (38+)

- `db['context']['context']` => Current context
- `db['context']['previous_contexts']` => Previous contexts
- `db['context']['next_contexts']` => Next contexts
- `db['context']['global_context']` => Global context
- `get_context(node, db)` => Infer context of given `node`

## General
Common gotchas

- `db['general']['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value

## Parentize
`parent` field to each node

- `parent_to(child, node)` => yields all parents of child until it reaches `node`

## Upgrade
Improvable (for 3.7+) syntaxes


### Django
`django` integration


### Unimport
`unimport` integration

- `db["community"]["unimport"]["unimport"]` => A list of imports that are not used
