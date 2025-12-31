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
