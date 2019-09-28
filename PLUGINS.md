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
Unreacable except finder

- `db['user_exceptions']` => A mapping of user-defined exceptions with name:tree_value
- Checks if an except statement is unreachable due to a more broad except

## Upgradeable
Finds syntaxes that can be improvable (for 3.8+)

- Checks if a yield can be replaced with yield from
- Checks if `super()` called with arguments (old style)

## Misc
Common gotchas

- Checks if a default argument is something mutable

### Unimport
`unimport` integration to InspectorTiger

- `db['unimport']` => A list of imports that are not used
- Checks if an import is not used through `unimport`
