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

// Allow some pedantic clippy lints that are too strict for this crate
#![allow(clippy::fn_params_excessive_bools)]
#![allow(clippy::must_use_candidate)]
#![allow(clippy::use_self)]
#![allow(clippy::doc_markdown)]
#![allow(clippy::missing_errors_doc)]
#![allow(clippy::missing_panics_doc)]
#![allow(clippy::module_name_repetitions)]
#![allow(clippy::uninlined_format_args)]

pub mod api;
pub mod services;
pub mod utils;

pub use api::ilinks::{ILinks, LinkConstants};
pub use api::recursive_links::RecursiveLinks;
pub use services::auth_storage_service::AuthStorageService;
pub use services::link_db_service::LinkDBService;
pub use services::menu_storage_service::MenuStorageService;
