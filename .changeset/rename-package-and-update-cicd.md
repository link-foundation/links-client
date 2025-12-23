---
'@link-foundation/links-client': major
---

Rename package from `@unidel2035/links-client` to `@link-foundation/links-client`. Split CI/CD into separate js.yml and python.yml workflows following link-foundation templates.

**Breaking Changes:**
- Package renamed from `@unidel2035/links-client` to `@link-foundation/links-client`

**Improvements:**
- Separate CI/CD workflows for JavaScript (js.yml) and Python (python.yml)
- Workflows follow latest best practices from link-foundation templates
- Added manual release support via workflow_dispatch
