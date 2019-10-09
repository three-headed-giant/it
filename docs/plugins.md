# Plugins
InspectorTiger plugins


## Misc
Common gotchas

- `db['unreachable_except']['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value

## Upgradeable
Improvable (for 3.8+) syntaxes


## Context
Context management for AST (38+)

- `db['context']['context']` => Current context
- `db['context']['previous_contexts']` => Previous contexts
- `db['context']['next_contexts']` => Next contexts
- `db['context']['global_context']` => Global context
- `get_context(node, db)` => Infer context of given `node`

## Parentize
`parent` field to each node

- `parent_to(child, node)` => yields all parents of child until it reaches `node`

### Unimport
`unimport` integration

- `db["community"]["unimport"]["unimport"]` => A list of imports that are not used
