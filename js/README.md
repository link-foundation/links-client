# Links Client - JavaScript/Node.js Implementation

Node.js client library for [link-cli](https://github.com/link-foundation/link-cli) — implementation of Links Theory database.

## Installation

### Prerequisites

Install link-cli globally:
```bash
dotnet tool install --global clink
```

### Package Installation

```bash
npm install @unidel2035/links-client
```

Or use GitHub directly:

```bash
npm install git+https://github.com/link-foundation/links-client.git
```

## Usage

### Basic Usage

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

### Menu Storage

```javascript
import { MenuStorageService } from '@unidel2035/links-client';

const menuStorage = new MenuStorageService();

const menu = [
  {
    label: "Dashboard",
    icon: "pi pi-home",
    to: "/dashboard",
    items: [
      { label: "Analytics", to: "/dashboard/analytics" }
    ]
  }
];

await menuStorage.storeMenuStructure(menu, 0);
const retrievedMenu = await menuStorage.getMenuStructure(0);
```

### Authentication Storage

```javascript
import { AuthStorageService } from '@unidel2035/links-client';

const authStorage = new AuthStorageService();

// Create user
const user = await authStorage.createUser({
  username: "alice",
  email: "alice@example.com"
});

// Set password
await authStorage.setPassword(user.userId, {
  hash: "hashed_password",
  salt: "random_salt"
});
```

## API

For detailed API documentation, see the docs/ directory.

## Examples

See examples in the examples/ directory:

- `basic-usage.js` - Basic clink integration tests
- `menu-storage.js` - Menu storage demonstration
- `auth-storage.js` - Authentication storage demonstration
- `integration.js` - Full integration example

## Testing

Run tests with Node.js test runner:

```bash
npm test
```

## License

The Unlicense

## Links

- Repository: https://github.com/link-foundation/links-client
- link-cli: https://github.com/link-foundation/link-cli
