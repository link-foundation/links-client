# Changelog Fragments

This directory contains changelog fragments for the Rust package.

## Adding a Changelog Entry

When making changes to this package, add a new markdown file in this directory with your changes.

### File Naming

Name your file descriptively, e.g., `add-new-feature.md` or `fix-parsing-bug.md`.

### File Format

Each fragment should contain:

1. A category header (one of: `### Added`, `### Changed`, `### Fixed`, `### Removed`)
2. A description of the change

Example:

```markdown
### Added

- New `get_children()` method for RecursiveLinks API
- Support for custom database paths
```

### Categories

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Fixed** - Bug fixes
- **Removed** - Removed features

## Release Process

When releasing a new version:
1. Fragments are collected and merged into CHANGELOG.md
2. Fragment files are deleted
3. Version is bumped in Cargo.toml
4. GitHub release is created
