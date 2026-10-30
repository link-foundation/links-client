#!/usr/bin/env bash
# Run from rust/. A registry lookup makes retries after bootstrap or release
# creation failures safe, without hiding authentication or publication errors.
set -euo pipefail

VERSION=$(cargo metadata --no-deps --format-version 1 --locked |
  jq -er '.packages[] | select(.name == "links-client") | .version')
STATUS=$(curl --silent --show-error --retry 3 --output /dev/null \
  --write-out '%{http_code}' \
  --user-agent 'links-client-release (https://github.com/link-foundation/links-client)' \
  "https://crates.io/api/v1/crates/links-client/$VERSION")

case "$STATUS" in
  200)
    echo "links-client $VERSION is already on crates.io; skipping upload."
    exit 0
    ;;
  404) ;;
  *)
    echo "::error::Unable to check links-client $VERSION on crates.io (HTTP $STATUS)."
    exit 1
    ;;
esac

if [ -z "${CARGO_REGISTRY_TOKEN:-}" ]; then
  echo "::error::crates.io authentication unavailable. Complete the first publish and register .github/workflows/rust.yml as a trusted publisher (see rust/README.md), or configure CARGO_REGISTRY_TOKEN / CARGO_TOKEN as a fallback."
  exit 1
fi

cargo publish --locked
