//! Tests for the ILinks API

use links_client::{ILinks, LinkConstants};
use links_client::services::link_db_service::Link;

#[test]
fn test_ilinks_creation() {
    let links = ILinks::new(None);
    assert!(links.is_ok());
}

#[test]
fn test_link_constants() {
    assert_eq!(LinkConstants::any_value(), 0);
    assert_ne!(LinkConstants::Continue, LinkConstants::Break);
}

#[test]
fn test_filter_with_any() {
    let links = ILinks::new(None).unwrap();

    // Test that we can create ILinks and the filter logic works
    // The actual filtering is tested in the ilinks module
    let constants = links.get_constants();
    assert!(matches!(constants, LinkConstants::Any));
}

// Integration tests that require clink are marked with ignore
// Run them with: cargo test -- --ignored

#[tokio::test]
#[ignore = "requires clink to be installed"]
async fn test_create_and_delete_link() {
    let links = ILinks::new(None).unwrap();

    // Create a link
    let link_id = links.create(&[100, 200], None::<fn(_)>).await.unwrap();
    assert!(link_id > 0);

    // Delete the link
    let deleted_id = links.delete(Some(&[link_id]), None::<fn(_)>).await.unwrap();
    assert_eq!(deleted_id, link_id);
}

#[tokio::test]
#[ignore = "requires clink to be installed"]
async fn test_count_links() {
    let links = ILinks::new(None).unwrap();

    // Count should work even if database is empty
    let count = links.count(None).await;
    assert!(count.is_ok());
}

#[tokio::test]
#[ignore = "requires clink to be installed"]
async fn test_each_with_handler() {
    let links = ILinks::new(None).unwrap();

    let mut count = 0;
    let result = links
        .each(None, Some(|_link: &Link| {
            count += 1;
            LinkConstants::Continue
        }))
        .await;

    assert!(result.is_ok());
}

#[tokio::test]
#[ignore = "requires clink to be installed"]
async fn test_each_with_break() {
    let links = ILinks::new(None).unwrap();

    // First create some links
    let id1 = links.create(&[1, 2], None::<fn(_)>).await.unwrap();
    let id2 = links.create(&[3, 4], None::<fn(_)>).await.unwrap();

    let mut visited = 0;
    let result = links
        .each(None, Some(|_link: &Link| {
            visited += 1;
            if visited >= 1 {
                LinkConstants::Break
            } else {
                LinkConstants::Continue
            }
        }))
        .await
        .unwrap();

    assert_eq!(result, LinkConstants::Break);

    // Cleanup
    let _ = links.delete(Some(&[id1]), None::<fn(_)>).await;
    let _ = links.delete(Some(&[id2]), None::<fn(_)>).await;
}
