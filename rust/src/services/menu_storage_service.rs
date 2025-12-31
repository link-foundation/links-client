//! `MenuStorageService` - Service for menu item storage

use std::path::PathBuf;
use thiserror::Error;
use tracing::{debug, error};

use super::link_db_service::{LinkDBError, LinkDBService};

/// Errors that can occur when using `MenuStorageService`
#[derive(Error, Debug)]
pub enum MenuStorageError {
    #[error("LinkDB error: {0}")]
    LinkDBError(#[from] LinkDBError),

    #[error("Menu item not found: {0}")]
    ItemNotFound(u64),
}

/// Menu item data structure
#[derive(Debug, Clone)]
pub struct MenuItem {
    /// Link ID in the database
    pub link_id: u64,
    /// Item ID
    pub item_id: u64,
    /// Parent ID (0 for root items)
    pub parent_id: u64,
}

/// `MenuStorageService` - Service for menu item storage
///
/// This service provides methods for storing and retrieving menu configuration
/// using the `LinkDB` backend.
pub struct MenuStorageService {
    db: LinkDBService,
    /// Type identifier for menu item links
    menu_type_id: u64,
}

impl MenuStorageService {
    /// Create a new `MenuStorageService` with the specified database path
    ///
    /// # Arguments
    ///
    /// * `db_path` - Optional path to the database file
    pub fn new(db_path: Option<PathBuf>) -> Self {
        Self {
            db: LinkDBService::new(db_path),
            menu_type_id: 1000, // Type identifier for menu items
        }
    }

    /// Store a menu item
    ///
    /// # Arguments
    ///
    /// * `item_id` - Unique item identifier
    /// * `parent_id` - Parent item ID (0 for root items)
    pub async fn store_menu_item(
        &self,
        item_id: u64,
        parent_id: u64,
    ) -> Result<MenuItem, MenuStorageError> {
        debug!("Storing menu item: id={}, parent={}", item_id, parent_id);

        // Create a link representing the menu item
        // source = item_id, target = menu_type_id
        let link = self.db.create_link(item_id, self.menu_type_id).await?;

        // If there's a parent, create a parent-child relationship link
        if parent_id > 0 {
            self.db.create_link(parent_id, item_id).await?;
        }

        Ok(MenuItem {
            link_id: link.id,
            item_id,
            parent_id,
        })
    }

    /// Get all menu items
    pub async fn get_all_menu_items(&self) -> Result<Vec<MenuItem>, MenuStorageError> {
        let all_links = self.db.read_all_links().await?;

        let items: Vec<MenuItem> = all_links
            .iter()
            .filter(|link| link.target == self.menu_type_id)
            .map(|link| MenuItem {
                link_id: link.id,
                item_id: link.source,
                parent_id: 0, // Would need additional lookup to get parent
            })
            .collect();

        Ok(items)
    }

    /// Get menu item by ID
    pub async fn get_menu_item(&self, item_id: u64) -> Result<Option<MenuItem>, MenuStorageError> {
        let all_links = self.db.read_all_links().await?;

        let item = all_links
            .into_iter()
            .find(|link| link.source == item_id && link.target == self.menu_type_id)
            .map(|link| MenuItem {
                link_id: link.id,
                item_id: link.source,
                parent_id: 0,
            });

        Ok(item)
    }

    /// Delete menu item by link ID
    pub async fn delete_menu_item(&self, link_id: u64) -> Result<bool, MenuStorageError> {
        self.db.delete_link(link_id).await?;
        Ok(true)
    }

    /// Clear all menu items
    pub async fn clear_all_menu_items(&self) -> Result<bool, MenuStorageError> {
        let all_links = self.db.read_all_links().await?;

        for link in all_links {
            if link.target == self.menu_type_id {
                if let Err(e) = self.db.delete_link(link.id).await {
                    error!("Failed to delete menu link {}: {}", link.id, e);
                }
            }
        }

        Ok(true)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_menu_storage_service_creation() {
        let service = MenuStorageService::new(None);
        assert_eq!(service.menu_type_id, 1000);
    }
}
