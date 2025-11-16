# Links Client - Python Implementation

Python client library for [link-cli](https://github.com/link-foundation/link-cli) — implementation of Links Theory database.

## Installation

### Prerequisites

Install link-cli globally:
```bash
dotnet tool install --global clink
```

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

Run tests with pytest:

```bash
pytest tests/
```

## License

The Unlicense

## Links

- Source repository: https://github.com/link-foundation/links-client
- link-cli: https://github.com/link-foundation/link-cli
