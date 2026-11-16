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

## Verification evidence

- Minimal clink probe: 4.0.6 rejects non-existent reference 1001; 2.2.2 creates the link.
- Locally passed 24 unit tests, 24 integration tests, five workflow checks, build, twine check, installed-wheel imports, and actionlint. The existing PyPI 1.0.0 wheel fails the import check with missing `links_client.api`.
- First PR run 43779552576 and dispatch 43779547142 passed tests and builds at 1e678c1. The dispatch exposed a second release blocker: skipped changelog ancestors cause release jobs to skip under the default job success condition. Regression checks reproduce the missing `always()` guard in all three release paths; explicit successful test/build result checks retain the release gates.
- After correcting the conditions, PR run [43780116788](https://github.com/link-foundation/links-client/actions/runs/43780116788) passes all checks at f12d5fa. Dispatch [43780111714](https://github.com/link-foundation/links-client/actions/runs/43780111714) passes Test Python and Build Package and reaches Publish to PyPI.
- **Blocked and unfinished:** PyPI rejects token exchange with `invalid-pending-publisher: valid token, but project already exists` (saved dispatch log lines 1331–1334). The pending publisher must be attached to the existing `links-client` project by its PyPI owner. Coordinates: `link-foundation`, `links-client`, `python.yml`, no environment. No PyPI credential variables, `.pypirc`, authenticated document sessions, or matching PyPI management plugin are available in this environment.
- Test/build acceptance is verified. Live OIDC publication and trusted-publisher attachment are not verified and remain unfinished. Do not retry the publish unchanged or merge this PR as though those criteria were completed. The README documents the account-side correction and rerun procedure.
