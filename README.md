# links-client

Client library for [link-cli](https://github.com/link-foundation/link-cli) — implementation of Links Theory database.

Available in **JavaScript** and **Python**.

## Language Implementations

This repository contains implementations in multiple languages:

- **[JavaScript/Node.js](js/)** - See [js/README.md](js/README.md) for JavaScript-specific documentation
- **[Python](python/)** - See [python/README.md](python/README.md) for Python-specific documentation

## Quick Start

### Prerequisites

Install link-cli globally:
```bash
dotnet tool install --global clink
```

### JavaScript/Node.js

```bash
cd js
npm install
```

```javascript
import { LinkDBService } from '@unidel2035/links-client';

const db = new LinkDBService('/path/to/database.links');

// Create a link
const link = await db.createLink(100, 200);
console.log(link); // { id: 1, source: 100, target: 200 }

// Read all links
const links = await db.readAllLinks();

// Delete a link
await db.deleteLink(1);
```

### Python

```bash
cd python
pip install -e .
```

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

## Features

Both implementations provide:

- **LinkDBService** - Core database operations (CRUD for links)
- **MenuStorageService** - Store and retrieve menu configurations
- **AuthStorageService** - Store authentication data (users, tokens, passwords)

## Repository Structure

```
links-client/
├── js/                 # JavaScript/Node.js implementation
│   ├── src/           # Source code
│   ├── examples/      # Usage examples
│   ├── tests/         # Test suite
│   ├── docs/          # Documentation
│   └── package.json   # NPM package configuration
├── python/            # Python implementation
│   ├── links_client/  # Package source code
│   ├── examples/      # Usage examples
│   ├── tests/         # Test suite
│   ├── docs/          # Documentation
│   └── pyproject.toml # Python package configuration
├── README.md          # This file
└── LICENSE            # The Unlicense

```

## Documentation

- JavaScript documentation: [js/docs/](js/docs/)
- Python documentation: [python/docs/](python/docs/)

## Examples

- JavaScript examples: [js/examples/](js/examples/)
- Python examples: [python/examples/](python/examples/)

## License

The Unlicense

## Links

- Repository: https://github.com/link-foundation/links-client
- link-cli: https://github.com/link-foundation/link-cli
- Links Notation: https://github.com/link-foundation/links-notation
