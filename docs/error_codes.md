# Error codes

- `DEFAULT_MUTABLE_ARG` => Default argument is something mutable.
- `UNREACHABLE_EXCEPT` => Except statement is unreachable due to a more broad except.
- `CONTROL_FLOW_INSIDE_FINALLY` => A return/break/continue that would implicitly cancel any active exception.
- `YIELD_FROM` => Yield can be replaced with yield from.
- `SUPER_ARGS` => `super()` called with arguments (old style).
- `OPTIONAL` => `Union[Type, None]` can be replaced with `Optional[Type]`.
- `UNUSED_IMPORT` => A module/name is imported but not used.
