### Fixed

- Pin clink 2.2.2 in Python CI to retain compatible implicit-reference queries.
- Separate unit tests from explicitly marked clink integration tests and isolate test databases.
- Include the API modules in built distributions and verify installed wheel imports before release.
- Retain clink failure output in opt-in debug logs and document PyPI OIDC publisher setup.
- Restrict manual releases to main, matching automatic releases.

### Added

- Explicit manual publishing of the tested current version from a selected ref without branch pushes.
