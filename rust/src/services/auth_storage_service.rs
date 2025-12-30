//! AuthStorageService - Service for user authentication data storage

use std::collections::HashMap;
use std::path::PathBuf;
use thiserror::Error;
use tracing::{debug, error};

use super::link_db_service::{LinkDBService, LinkDBError};

/// Errors that can occur when using AuthStorageService
#[derive(Error, Debug)]
pub enum AuthStorageError {
    #[error("LinkDB error: {0}")]
    LinkDBError(#[from] LinkDBError),

    #[error("User not found: {0}")]
    UserNotFound(String),

    #[error("Failed to parse user data: {0}")]
    ParseError(String),
}

/// User data structure
#[derive(Debug, Clone)]
pub struct User {
    /// User ID
    pub id: u64,
    /// Username
    pub username: String,
    /// Additional user data stored as key-value pairs
    pub data: HashMap<String, String>,
}

/// AuthStorageService - Service for user authentication data storage
///
/// This service provides methods for storing and retrieving user authentication data
/// using the LinkDB backend.
pub struct AuthStorageService {
    db: LinkDBService,
    /// Type identifier for user links
    user_type_id: u64,
}

impl AuthStorageService {
    /// Create a new AuthStorageService with the specified database path
    ///
    /// # Arguments
    ///
    /// * `db_path` - Optional path to the database file
    pub fn new(db_path: Option<PathBuf>) -> Self {
        Self {
            db: LinkDBService::new(db_path),
            user_type_id: 2000, // Type identifier for user data
        }
    }

    /// Store user data
    ///
    /// # Arguments
    ///
    /// * `user_id` - Unique user identifier
    /// * `username` - Username
    pub async fn store_user(&self, user_id: u64, _username: &str) -> Result<u64, AuthStorageError> {
        debug!("Storing user: id={}", user_id);

        // Create a link representing the user
        // source = user_id, target = user_type_id
        let link = self.db.create_link(user_id, self.user_type_id).await?;

        Ok(link.id)
    }

    /// Get all users
    pub async fn get_all_users(&self) -> Result<Vec<User>, AuthStorageError> {
        let all_links = self.db.read_all_links().await?;

        let users: Vec<User> = all_links
            .into_iter()
            .filter(|link| link.target == self.user_type_id)
            .map(|link| User {
                id: link.source,
                username: format!("user_{}", link.source),
                data: HashMap::new(),
            })
            .collect();

        Ok(users)
    }

    /// Get user by ID
    pub async fn get_user(&self, user_id: u64) -> Result<Option<User>, AuthStorageError> {
        let all_links = self.db.read_all_links().await?;

        let user = all_links
            .into_iter()
            .find(|link| link.source == user_id && link.target == self.user_type_id)
            .map(|link| User {
                id: link.source,
                username: format!("user_{}", link.source),
                data: HashMap::new(),
            });

        Ok(user)
    }

    /// Delete user by link ID
    pub async fn delete_user(&self, link_id: u64) -> Result<bool, AuthStorageError> {
        self.db.delete_link(link_id).await?;
        Ok(true)
    }

    /// Clear all user data
    pub async fn clear_all_users(&self) -> Result<bool, AuthStorageError> {
        let all_links = self.db.read_all_links().await?;

        for link in all_links {
            if link.target == self.user_type_id {
                if let Err(e) = self.db.delete_link(link.id).await {
                    error!("Failed to delete user link {}: {}", link.id, e);
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
    fn test_auth_storage_service_creation() {
        let service = AuthStorageService::new(None);
        assert_eq!(service.user_type_id, 2000);
    }
}
