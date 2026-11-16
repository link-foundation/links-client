# Issue 26 implementation and verification

- Read issue 26 and all PR 27 conversation, inline comments, and reviews: no additional feedback or sub-issues.
- Preserve the failed first-publish logs and identify the root cause. The workflow installed clink 4.0.6; 21 tests failed. The existing JavaScript workflow pins compatible clink 2.2.2.
- Pin the Python integration dependency, mark integration tests, remove subprocess calls during collection, and run unit tests independently of clink.
- Keep all existing test coverage and isolate integration databases so tests work individually.
- Add focused subprocess/error regression coverage and preserve debug diagnostics with tracing disabled by default.
- Include the omitted API package in the wheel and verify imports from an installed wheel outside the checkout.
- Prepare version 1.0.1 (1.0.0 already exists on PyPI), document trusted publishing, and retain OIDC release permissions.
- Run focused local checks, push only issue-26-beef2acf3878, and verify python.yml on the current commit.
- Verify live PyPI OIDC publication and publisher attachment separately from test success. If credentials or default-branch restrictions prevent verification, record exact unfinished criteria and evidence in PR 27.
- Review the final PR diff, verify main is included and the tree is clean, update the PR description and mark ready without merging.
