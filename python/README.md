# Links Client - Python Implementation

Python client library for [link-cli](https://github.com/link-foundation/link-cli) — implementation of Links Theory database.

## Installation

### Prerequisites

Install link-cli globally:
```bash
dotnet tool install --global clink --version 2.2.2
```

Use .NET 8 and clink 2.2.2. Later clink releases reject the implicit references
used by the current client's creation queries.

### Package Installation

```bash
pip install -e .
```

Or install from the repository root:

```bash
cd python
pip install -e .
```

## Usage

### Basic Usage

```python
from links_client import LinkDBService

db = LinkDBService('/path/to/database.links')

# Create a link
link = db.create_link(100, 200)
print(link)  # {'id': 1, 'source': 100, 'target': 200}

# Read all links
links = db.read_all_links()

# Delete a link
db.delete_link(1)
```

### Menu Storage

```python
from links_client import MenuStorageService

menu_storage = MenuStorageService()

menu = [
    {
        "label": "Dashboard",
        "icon": "pi pi-home",
        "to": "/dashboard",
        "items": [
            {"label": "Analytics", "to": "/dashboard/analytics"}
        ]
    }
]

menu_storage.store_menu_structure(menu, 0)
retrieved_menu = menu_storage.get_menu_structure(0)
```

### Authentication Storage

```python
from links_client import AuthStorageService

auth_storage = AuthStorageService()

# Create user
user = auth_storage.create_user({
    "username": "alice",
    "email": "alice@example.com"
})

# Set password
auth_storage.set_password(user['userId'], {
    "hash": "hashed_password",
    "salt": "random_salt"
})
```

## API

For detailed API documentation, see the docs/ directory.

## Examples

See examples in the examples/ directory:

- `basic_usage.py` - Basic clink integration tests
- `menu_storage_example.py` - Menu storage demonstration
- `auth_storage_example.py` - Authentication storage demonstration

## Testing

Install test dependencies and run unit tests without .NET or clink:

```bash
pip install -e ".[dev]"
pytest
```

Tests that launch clink are marked `integration` and excluded by default.
Install clink as described above, then select them explicitly:

```bash
pytest -m integration
```

To run both groups: `pytest -m ""`. Explicit integration runs fail if clink is
missing or has an incompatible version. Each test uses its own temporary database;
unit tests reject unmocked subprocess calls. CI runs unit tests before installing
clink, then runs every integration test with the pinned binary.

## PyPI releases

The `Python CI/CD` workflow tests and builds the package on pull requests. It also
installs the wheel into a fresh environment and checks every public import.
Version 1.0.1 is the next release after the existing PyPI 1.0.0 bootstrap upload.

All release jobs use `pypa/gh-action-pypi-publish` with `id-token: write`, without
a PyPI password or API token. On `main`, pushing a new package version triggers
auto-release; a manual dispatch bumps the version and publishes it.

For an intentional release from a selected ref, dispatch with `publish_current`
enabled. This publishes the existing version from the tested build artifacts,
without changing any branch, and creates a release tag at the tested commit.
Choose a version that is not already on PyPI. The normal manual version-bump
job is disabled in this mode. This also allows verification of OIDC before merge.

The PyPI project owner must attach this trusted publisher at
https://pypi.org/manage/project/links-client/settings/publishing/:

- Owner: `link-foundation`
- Repository: `links-client`
- Workflow: `python.yml`
- Environment: leave empty (the release jobs do not declare one)

If publishing reports `invalid-pending-publisher: valid token, but project already
exists`, the publisher is still registered for creation of a new project. Since
`links-client` already exists, its owner must add the publisher on the existing
project's publishing settings page above. A pending publisher alone cannot
authorize uploads to that project. After attachment, repeat a dispatch with
`publish_current` enabled to publish the prepared version.

See [PyPI's publisher setup instructions](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).
Confirm attachment by inspecting that settings page and a successful `Publish to
PyPI` step using OIDC. A passing test/build job or a manually uploaded package
does not establish that trusted publishing works. PyPI file provenance provides
public evidence for releases uploaded with attestations.

## License

The Unlicense

## Links

- Source repository: https://github.com/link-foundation/links-client
- link-cli: https://github.com/link-foundation/link-cli
