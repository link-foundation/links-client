//! Links Client - Rust client library for link-cli (Links Theory database)
//!
//! This crate provides a Rust interface to the link-cli (clink) tool for
//! working with Links Theory databases.
//!
//! # Example
//!
//! ```no_run
//! use links_client::{ILinks, LinkConstants};
//! use links_client::api::ilinks::LinkChange;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let links = ILinks::new(None)?;
//!
//!     // Create a link
//!     let link_id = links.create(&[1, 2], None::<fn(LinkChange)>).await?;
//!     println!("Created link: {}", link_id);
//!
//!     // Count all links
//!     let count = links.count(None).await?;
//!     println!("Total links: {}", count);
//!
//!     Ok(())
//! }
//! ```

pub mod api;
pub mod services;
pub mod utils;

pub use api::ilinks::{ILinks, LinkConstants};
pub use api::recursive_links::RecursiveLinks;
pub use services::link_db_service::LinkDBService;
pub use services::auth_storage_service::AuthStorageService;
pub use services::menu_storage_service::MenuStorageService;
