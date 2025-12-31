//! `ILinks` - Universal flat API compatible with Platform.Data `ILinks` interface

use std::path::PathBuf;
use thiserror::Error;
use tracing::debug;

use crate::services::link_db_service::{Link, LinkDBError, LinkDBService};

/// Errors that can occur when using `ILinks`
#[derive(Error, Debug)]
pub enum ILinksError {
    #[error("LinkDB error: {0}")]
    LinkDBError(#[from] LinkDBError),

    #[error("Invalid substitution: {0}")]
    InvalidSubstitution(String),

    #[error("Invalid restriction: {0}")]
    InvalidRestriction(String),

    #[error("No links found matching restriction")]
    NoLinksFound,
}

/// Constants for `ILinks` operations
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LinkConstants {
    /// Continue iteration
    Continue,
    /// Break iteration
    Break,
    /// Match any value in restrictions (represented as 0)
    Any,
}

impl LinkConstants {
    /// Get the numeric value for Any constant
    #[must_use]
    pub const fn any_value() -> u64 {
        0
    }
}

/// Change notification for handlers
#[derive(Debug, Clone)]
pub struct LinkChange {
    /// Link state before the change (None for create)
    pub before: Option<Link>,
    /// Link state after the change (None for delete)
    pub after: Option<Link>,
}

/// `ILinks` - Universal flat Turing complete API for Links
/// Compatible with <https://github.com/linksplatform/Data/blob/main/csharp/Platform.Data/ILinks.cs>
///
/// Flat meaning it only works with a single link at a time.
pub struct ILinks {
    db: LinkDBService,
}

impl ILinks {
    /// Create a new `ILinks` instance
    ///
    /// # Arguments
    ///
    /// * `db_path` - Optional path to the database file
    pub fn new(db_path: Option<PathBuf>) -> Result<Self, ILinksError> {
        Ok(Self {
            db: LinkDBService::new(db_path),
        })
    }

    /// Get constants for this Links instance
    #[must_use]
    pub const fn get_constants(&self) -> LinkConstants {
        LinkConstants::Any
    }

    /// Count links matching the restriction
    ///
    /// # Arguments
    ///
    /// * `restriction` - Array to filter links, None for all
    ///   - `[id]` - match by ID
    ///   - `[source, target]` - match by source and target
    ///   - `[id, source, target]` - match all three
    pub async fn count(&self, restriction: Option<&[u64]>) -> Result<usize, ILinksError> {
        let all_links = self.db.read_all_links().await?;

        if restriction.is_none() || restriction.map_or(true, <[u64]>::is_empty) {
            return Ok(all_links.len());
        }

        let filtered = Self::filter_links(&all_links, restriction);
        Ok(filtered.len())
    }

    /// Iterate through links matching restriction, calling handler for each
    ///
    /// # Arguments
    ///
    /// * `restriction` - Array to filter links, None for all
    /// * `handler` - Callback function that returns Continue or Break
    pub async fn each<F>(
        &self,
        restriction: Option<&[u64]>,
        mut handler: Option<F>,
    ) -> Result<LinkConstants, ILinksError>
    where
        F: FnMut(&Link) -> LinkConstants,
    {
        let all_links = self.db.read_all_links().await?;
        let filtered = Self::filter_links(&all_links, restriction);

        if let Some(ref mut h) = handler {
            for link in filtered {
                let result = h(&link);
                if result == LinkConstants::Break {
                    return Ok(LinkConstants::Break);
                }
            }
        }

        Ok(LinkConstants::Continue)
    }

    /// Create a new link
    ///
    /// # Arguments
    ///
    /// * `substitution` - Array `[source, target]` or `[id, source, target]`
    /// * `handler` - Optional callback for change notification
    pub async fn create<F>(
        &self,
        substitution: &[u64],
        mut handler: Option<F>,
    ) -> Result<u64, ILinksError>
    where
        F: FnMut(LinkChange),
    {
        if substitution.len() < 2 {
            return Err(ILinksError::InvalidSubstitution(
                "Substitution must contain at least [source, target]".to_string(),
            ));
        }

        let (source, target) = (substitution[0], substitution[1]);
        debug!("Creating link: source={}, target={}", source, target);

        let link = self.db.create_link(source, target).await?;

        if let Some(ref mut h) = handler {
            h(LinkChange {
                before: None,
                after: Some(link.clone()),
            });
        }

        Ok(link.id)
    }

    /// Update existing links matching restriction
    ///
    /// # Arguments
    ///
    /// * `restriction` - Array to filter links to update
    /// * `substitution` - New values `[source, target]` or `[id, source, target]`
    /// * `handler` - Optional callback for change notification
    pub async fn update<F>(
        &self,
        restriction: Option<&[u64]>,
        substitution: &[u64],
        mut handler: Option<F>,
    ) -> Result<u64, ILinksError>
    where
        F: FnMut(LinkChange),
    {
        if restriction.is_none() || restriction.map_or(true, <[u64]>::is_empty) {
            return Err(ILinksError::InvalidRestriction(
                "Restriction required for update".to_string(),
            ));
        }

        if substitution.len() < 2 {
            return Err(ILinksError::InvalidSubstitution(
                "Substitution must contain at least [source, target]".to_string(),
            ));
        }

        let all_links = self.db.read_all_links().await?;
        let filtered = Self::filter_links(&all_links, restriction);

        if filtered.is_empty() {
            return Err(ILinksError::NoLinksFound);
        }

        // Update first matching link
        let link_to_update = &filtered[0];
        let (new_source, new_target) = if substitution.len() == 2 {
            (substitution[0], substitution[1])
        } else {
            (substitution[1], substitution[2])
        };

        let before = link_to_update.clone();
        let updated = self
            .db
            .update_link(link_to_update.id, new_source, new_target)
            .await?;

        if let Some(ref mut h) = handler {
            h(LinkChange {
                before: Some(before),
                after: Some(updated.clone()),
            });
        }

        Ok(updated.id)
    }

    /// Delete links matching restriction
    ///
    /// # Arguments
    ///
    /// * `restriction` - Array to filter links to delete
    /// * `handler` - Optional callback for change notification
    pub async fn delete<F>(
        &self,
        restriction: Option<&[u64]>,
        mut handler: Option<F>,
    ) -> Result<u64, ILinksError>
    where
        F: FnMut(LinkChange),
    {
        if restriction.is_none() || restriction.map_or(true, <[u64]>::is_empty) {
            return Err(ILinksError::InvalidRestriction(
                "Restriction required for delete".to_string(),
            ));
        }

        let all_links = self.db.read_all_links().await?;
        let filtered = Self::filter_links(&all_links, restriction);

        if filtered.is_empty() {
            return Err(ILinksError::NoLinksFound);
        }

        // Delete first matching link
        let link_to_delete = &filtered[0];
        let before = link_to_delete.clone();

        self.db.delete_link(link_to_delete.id).await?;

        if let Some(ref mut h) = handler {
            h(LinkChange {
                before: Some(before.clone()),
                after: None,
            });
        }

        Ok(before.id)
    }

    /// Helper method to filter links based on restriction
    fn filter_links(links: &[Link], restriction: Option<&[u64]>) -> Vec<Link> {
        let restriction = match restriction {
            Some(r) if !r.is_empty() => r,
            _ => return links.to_vec(),
        };

        let any = LinkConstants::any_value();

        links
            .iter()
            .filter(|link| {
                match restriction.len() {
                    1 => {
                        // [id] - match by ID
                        restriction[0] == any || link.id == restriction[0]
                    }
                    2 => {
                        // [source, target] - match by source and target
                        (restriction[0] == any || link.source == restriction[0])
                            && (restriction[1] == any || link.target == restriction[1])
                    }
                    _ => {
                        // [id, source, target] - match all three
                        (restriction[0] == any || link.id == restriction[0])
                            && (restriction[1] == any || link.source == restriction[1])
                            && (restriction[2] == any || link.target == restriction[2])
                    }
                }
            })
            .cloned()
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_link_constants() {
        assert_eq!(LinkConstants::any_value(), 0);
    }

    #[test]
    fn test_filter_links() {
        let all_links = vec![
            Link {
                id: 1,
                source: 2,
                target: 3,
            },
            Link {
                id: 2,
                source: 4,
                target: 5,
            },
            Link {
                id: 3,
                source: 2,
                target: 6,
            },
        ];

        // Filter by ID
        let filtered = ILinks::filter_links(&all_links, Some(&[1]));
        assert_eq!(filtered.len(), 1);
        assert_eq!(filtered[0].id, 1);

        // Filter by source and target
        let filtered = ILinks::filter_links(&all_links, Some(&[2, 3]));
        assert_eq!(filtered.len(), 1);
        assert_eq!(filtered[0].id, 1);

        // Filter with Any source
        let filtered = ILinks::filter_links(&all_links, Some(&[0, 3]));
        assert_eq!(filtered.len(), 1);

        // No restriction returns all
        let filtered = ILinks::filter_links(&all_links, None);
        assert_eq!(filtered.len(), 3);
    }
}
