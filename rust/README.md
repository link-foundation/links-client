# Links Client (Rust)

Rust client library for link-cli (Links Theory database).

This crate provides a Rust interface to the link-cli (clink) tool for working with Links Theory databases.

## Installation

Add this to your `Cargo.toml`:

```toml
[dependencies]
links-client = "1.0.0"
```

## Prerequisites

You need to have `clink` (link-cli) installed and available in your PATH:

```bash
dotnet tool install --global clink
```

## Usage

### ILinks API

The `ILinks` API provides a flat, Turing-complete interface for working with links:

```rust
use links_client::{ILinks, LinkConstants};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let links = ILinks::new(None)?;

    // Create a link (source: 1, target: 2)
    let link_id = links.create(&[1, 2], None).await?;
    println!("Created link: {}", link_id);

    // Count all links
    let count = links.count(None).await?;
    println!("Total links: {}", count);

    // Iterate over links
    links.each(None, Some(|link| {
        println!("Link: {:?}", link);
        LinkConstants::Continue
    })).await?;

    // Delete a link
    links.delete(Some(&[link_id]), None::<fn(_)>).await?;

    Ok(())
}
```

### RecursiveLinks API

The `RecursiveLinks` API provides methods for working with hierarchical link structures:

```rust
use links_client::RecursiveLinks;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let links = RecursiveLinks::new(None);

    // Create a parent-child relationship
    let parent = links.create_link(0, 0).await?;
    let child = links.create_link(parent.id, 0).await?;

    // Build a tree from a root
    if let Some(tree) = links.build_tree(parent.id).await? {
        println!("Tree has {} nodes", links.count_nodes(&tree));
    }

    Ok(())
}
```

### LinkDBService

For lower-level database operations:

```rust
use links_client::LinkDBService;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let db = LinkDBService::new(None);

    // Create a link
    let link = db.create_link(1, 2).await?;
    println!("Created: {:?}", link);

    // Read all links
    let all = db.read_all_links().await?;
    println!("Total links: {}", all.len());

    // Update a link
    let updated = db.update_link(link.id, 3, 4).await?;
    println!("Updated: {:?}", updated);

    // Delete a link
    db.delete_link(link.id).await?;

    Ok(())
}
```

## API Reference

### ILinks

- `new(db_path: Option<PathBuf>)` - Create a new ILinks instance
- `count(restriction: Option<&[u64]>)` - Count links matching restriction
- `each(restriction, handler)` - Iterate over matching links
- `create(substitution, handler)` - Create a new link
- `update(restriction, substitution, handler)` - Update matching links
- `delete(restriction, handler)` - Delete matching links

### RecursiveLinks

- `new(db_path: Option<PathBuf>)` - Create a new RecursiveLinks instance
- `get_all_links()` - Get all links as a flat list
- `get_children(parent_id)` - Get child links
- `get_parents(child_id)` - Get parent links
- `build_tree(root_id)` - Build a tree from a root link
- `create_link(source, target)` - Create a link
- `delete_link(id, recursive)` - Delete a link (optionally with children)

### LinkDBService

- `new(db_path: Option<PathBuf>)` - Create a new service instance
- `create_link(source, target)` - Create a link
- `read_all_links()` - Read all links
- `read_link(id)` - Read a specific link
- `update_link(id, source, target)` - Update a link
- `delete_link(id)` - Delete a link

## License

Unlicense - see [LICENSE](../LICENSE)

## Publishing to crates.io

This crate is intended for crates.io. The `Rust CI/CD` workflow
(`.github/workflows/rust.yml`) checks the package with
`cargo publish --dry-run --locked` on pull requests without registry credentials.
Both automatic releases (an unreleased version on `main`) and manual version
bumps (dispatch the workflow on `main`) publish to crates.io before creating the
`rust-v<version>` GitHub release. The initial version is `1.0.0`.
An existing version on crates.io is skipped, allowing recovery after bootstrap
or a failed GitHub release creation. Registry lookup and upload errors fail the
release rather than being treated as a successful publication.

Release jobs first request a short-lived token with
[`rust-lang/crates-io-auth-action`](https://github.com/rust-lang/crates-io-auth-action)
and `id-token: write`. If OIDC is unavailable, they use the existing
`CARGO_REGISTRY_TOKEN` secret, then `CARGO_TOKEN`. These fallback secrets remain
optional and are not deleted. If all authentication methods are unavailable,
the release fails with setup instructions.

### First release and trusted publisher registration

crates.io requires an initial token-authenticated publish before a crate can
register a trusted publisher. After merging the workflow, run the following
from an authenticated maintainer environment with
[`package-registry-manager`](https://github.com/link-foundation/package-registry-manager)
installed:

```bash
package-registry-manager setup --repository . --registry crates-io --execute
```

The setup tool validates the package, publishes the first version from the
default branch using a short-lived crate-scoped token, registers the trusted
publisher, then revokes and verifies revocation of the bootstrap token. Keep
existing fallback secrets; do not opt into deleting token secrets.

Configure the trusted publisher for:

- GitHub owner: `link-foundation`
- Repository: `links-client`
- Workflow filename: `rust.yml` (in `.github/workflows/`)
- Environment: leave empty (these release jobs do not use an environment)

Subsequent CI releases use OIDC without a stored token. Verify the first release
and publisher in the crate's crates.io settings before considering setup
complete. Registry authentication and publisher registration cannot be verified
by a PR dry run.

To run the workflow regression checks locally:

```bash
python -m pip install PyYAML==6.0.3
python -m unittest discover -s experiments -p 'test_rust_release.py' -v
```

Run these commands from the repository root. The checks cover both release paths,
OIDC permissions, token fallback, publication ordering, and credential-free PR
validation.
