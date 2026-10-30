### Added

- Publish Rust releases to crates.io using trusted publishing (OIDC) first,
  with optional `CARGO_REGISTRY_TOKEN` / `CARGO_TOKEN` fallback.
- Validate the publishable package and release authentication policy in PR CI.
- Document initial publication and trusted publisher registration.

### Fixed

- Keep Cargo.lock synchronized during manual version bumps for locked publishing.
- Restrict manual Rust releases to main.
- Skip already published versions on retries while surfacing registry and upload errors.
- Keep the empty-output test compatible with current Clippy assertion diagnostics.
