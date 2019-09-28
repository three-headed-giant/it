# Changelog
All notable changes to this project will be documented in this file.

## [0.6.0] - Unrelased
### Core
- Handler priority system with `utils.Priority` decorator
- New event (`utils.Events.NODE_FINALIZE`) for doing work after all handlers called and node traversed
- Instead of reportme, reports are now in JSON format ([#2](https://github.com/thg-consulting/inspectortiger/issues/2))
- Severity level system removed (eg `@Level.AVG`) ([#3](https://github.com/thg-consulting/inspectortiger/issues/3))
- Report grouping changed to plugins instead of levels ([#3](https://github.com/thg-consulting/inspectortiger/issues/3))
### Plugins
#### Context
- Context management improved with scope finalizing
#### Upgradeable
- Implemented a handler for old `super` usage with arguments
