# Changelog
All notable changes to this project will be documented in this file.

## [0.6.0] - Unrelased
### Core
- Handler priority system with `utils.Priority` decorator
- New event (`utils.Events.NODE_FINALIZE`) for doing work after all handlers called and node traversed
### Plugins
#### Context
- Context management improved with scope finalizing
#### Upgradeable
- Implemented a handler for old `super` usage with arguments
