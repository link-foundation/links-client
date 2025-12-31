//! API modules for the Links Client library

pub mod ilinks;
pub mod recursive_links;

pub use ilinks::{ILinks, LinkConstants};
pub use recursive_links::RecursiveLinks;
