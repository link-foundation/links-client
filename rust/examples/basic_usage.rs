//! Basic usage example for the Links Client library

use links_client::{ILinks, LinkConstants};
use links_client::services::link_db_service::Link;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Links Client - Basic Usage Example\n");

    // Note: This example requires clink (link-cli) to be installed
    // Install with: dotnet tool install --global clink

    // Create an ILinks instance with default database path
    let links = match ILinks::new(None) {
        Ok(l) => l,
        Err(e) => {
            eprintln!("Failed to create ILinks: {}", e);
            eprintln!("\nMake sure clink is installed:");
            eprintln!("  dotnet tool install --global clink");
            return Ok(());
        }
    };

    println!("ILinks instance created successfully");

    // Count existing links
    match links.count(None).await {
        Ok(count) => println!("Current link count: {}", count),
        Err(e) => {
            eprintln!("Failed to count links: {}", e);
            eprintln!("\nThis error usually means clink is not installed or not in PATH.");
            return Ok(());
        }
    }

    // Create a new link
    println!("\nCreating a link (source: 1, target: 2)...");
    let link_id = links.create(&[1, 2], None::<fn(_)>).await?;
    println!("Created link with ID: {}", link_id);

    // Count again
    let count = links.count(None).await?;
    println!("Link count after create: {}", count);

    // Iterate over all links
    println!("\nIterating over all links:");
    links
        .each(None, Some(|link: &Link| {
            println!("  Link {}: {} -> {}", link.id, link.source, link.target);
            LinkConstants::Continue
        }))
        .await?;

    // Update the link
    println!("\nUpdating link to (source: 10, target: 20)...");
    links.update(Some(&[link_id]), &[10, 20], None::<fn(_)>).await?;
    println!("Link updated");

    // Iterate again to see the change
    println!("\nLinks after update:");
    links
        .each(None, Some(|link: &Link| {
            println!("  Link {}: {} -> {}", link.id, link.source, link.target);
            LinkConstants::Continue
        }))
        .await?;

    // Delete the link
    println!("\nDeleting the link...");
    links.delete(Some(&[link_id]), None::<fn(_)>).await?;
    println!("Link deleted");

    // Final count
    let count = links.count(None).await?;
    println!("\nFinal link count: {}", count);

    println!("\nExample completed successfully!");
    Ok(())
}
