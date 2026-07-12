# @link-foundation/links-client

## 1.2.0

### Minor Changes

- 69f0901: Add TypeScript declarations for the JavaScript package's public API.

## 1.1.0

### Minor Changes

- bb1b02f: Add per-language CI/CD workflows and Rust translation

  **New Features:**

  - Added Rust translation of the links-client library with full API parity
  - Per-language versioning: JavaScript uses .changeset, Python/Rust use changelog.d

  **CI/CD Improvements:**

  - Moved JavaScript .changeset to js/.changeset folder
  - Added rust.yml workflow for Rust CI/CD
  - Added changelog.d support to Python and Rust workflows
  - Added path filtering to all workflows for better efficiency
  - Each language can now release independently
