//! `RecursiveLinks` - Recursive API for working with hierarchical link structures

use std::future::Future;
use std::path::PathBuf;
use std::pin::Pin;
use thiserror::Error;
use tracing::debug;

use crate::services::link_db_service::{Link, LinkDBError, LinkDBService};

/// Errors that can occur when using `RecursiveLinks`
#[derive(Error, Debug)]
pub enum RecursiveLinksError {
    #[error("LinkDB error: {0}")]
    LinkDBError(#[from] LinkDBError),

    #[error("Link not found: {0}")]
    LinkNotFound(u64),

    #[error("Maximum recursion depth exceeded")]
    MaxDepthExceeded,
}

/// A node in a recursive link tree
#[derive(Debug, Clone)]
pub struct LinkNode {
    /// The link data
    pub link: Link,
    /// Child links
    pub children: Vec<LinkNode>,
}

/// `RecursiveLinks` - API for working with hierarchical link structures
///
/// This API provides methods for traversing and manipulating link trees,
/// where links can form parent-child relationships.
pub struct RecursiveLinks {
    db: LinkDBService,
    /// Maximum recursion depth for tree traversal
    max_depth: usize,
}

impl RecursiveLinks {
    /// Create a new `RecursiveLinks` instance
    ///
    /// # Arguments
    ///
    /// * `db_path` - Optional path to the database file
    #[must_use]
    pub fn new(db_path: Option<PathBuf>) -> Self {
        Self {
            db: LinkDBService::new(db_path),
            max_depth: 100, // Default max depth
        }
    }

    /// Set the maximum recursion depth
    pub fn set_max_depth(&mut self, depth: usize) {
        self.max_depth = depth;
    }

    /// Get all links as a flat list
    pub async fn get_all_links(&self) -> Result<Vec<Link>, RecursiveLinksError> {
        Ok(self.db.read_all_links().await?)
    }

    /// Get links where the given link is the source
    pub async fn get_children(&self, parent_id: u64) -> Result<Vec<Link>, RecursiveLinksError> {
        let all_links = self.db.read_all_links().await?;
        Ok(all_links
            .into_iter()
            .filter(|l| l.source == parent_id)
            .collect())
    }

    /// Get links where the given link is the target
    pub async fn get_parents(&self, child_id: u64) -> Result<Vec<Link>, RecursiveLinksError> {
        let all_links = self.db.read_all_links().await?;
        Ok(all_links
            .into_iter()
            .filter(|l| l.target == child_id)
            .collect())
    }

    /// Build a tree starting from the given root link
    ///
    /// # Arguments
    ///
    /// * `root_id` - The ID of the root link
    pub async fn build_tree(&self, root_id: u64) -> Result<Option<LinkNode>, RecursiveLinksError> {
        let link = self.db.read_link(root_id).await?;

        match link {
            Some(link) => {
                let node = self.build_tree_impl(link, 0).await?;
                Ok(Some(node))
            }
            None => Ok(None),
        }
    }

    /// Recursively build a tree node (using `Box::pin` for async recursion)
    fn build_tree_impl<'a>(
        &'a self,
        link: Link,
        depth: usize,
    ) -> Pin<Box<dyn Future<Output = Result<LinkNode, RecursiveLinksError>> + Send + 'a>> {
        Box::pin(async move {
            if depth >= self.max_depth {
                return Err(RecursiveLinksError::MaxDepthExceeded);
            }

            debug!("Building tree node for link {} at depth {}", link.id, depth);

            // Get children (links where this link's id is the source)
            let children_links = self.get_children(link.id).await?;

            let mut children = Vec::new();
            for child_link in children_links {
                // Recursively build children
                let child_node = self.build_tree_impl(child_link, depth + 1).await?;
                children.push(child_node);
            }

            Ok(LinkNode { link, children })
        })
    }

    /// Create a link
    pub async fn create_link(&self, source: u64, target: u64) -> Result<Link, RecursiveLinksError> {
        Ok(self.db.create_link(source, target).await?)
    }

    /// Delete a link and optionally all its children
    pub async fn delete_link(&self, id: u64, recursive: bool) -> Result<bool, RecursiveLinksError> {
        if recursive {
            self.delete_link_impl(id).await?;
        } else {
            self.db.delete_link(id).await?;
        }
        Ok(true)
    }

    /// Recursively delete a link and its children (using `Box::pin` for async recursion)
    fn delete_link_impl<'a>(
        &'a self,
        id: u64,
    ) -> Pin<Box<dyn Future<Output = Result<(), RecursiveLinksError>> + Send + 'a>> {
        Box::pin(async move {
            // First delete all children
            let children = self.get_children(id).await?;
            for child in children {
                self.delete_link_impl(child.id).await?;
            }

            self.db.delete_link(id).await?;
            Ok(())
        })
    }

    /// Count all links in a tree starting from the given root
    pub async fn count_tree(&self, root_id: u64) -> Result<usize, RecursiveLinksError> {
        let tree = self.build_tree(root_id).await?;
        Ok(tree.map_or(0, |node| Self::count_nodes(&node)))
    }

    /// Recursively count nodes in a tree
    #[must_use]
    pub fn count_nodes(node: &LinkNode) -> usize {
        let mut count = 1; // Count this node
        for child in &node.children {
            count += Self::count_nodes(child);
        }
        count
    }

    /// Flatten a tree into a list of links (depth-first order)
    #[must_use]
    pub fn flatten_tree(node: &LinkNode) -> Vec<Link> {
        let mut result = vec![node.link.clone()];
        for child in &node.children {
            result.extend(Self::flatten_tree(child));
        }
        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_recursive_links_creation() {
        let links = RecursiveLinks::new(None);
        assert_eq!(links.max_depth, 100);
    }

    #[test]
    fn test_set_max_depth() {
        let mut links = RecursiveLinks::new(None);
        links.set_max_depth(50);
        assert_eq!(links.max_depth, 50);
    }

    #[test]
    fn test_count_nodes() {
        let tree = LinkNode {
            link: Link {
                id: 1,
                source: 0,
                target: 0,
            },
            children: vec![
                LinkNode {
                    link: Link {
                        id: 2,
                        source: 1,
                        target: 0,
                    },
                    children: vec![],
                },
                LinkNode {
                    link: Link {
                        id: 3,
                        source: 1,
                        target: 0,
                    },
                    children: vec![LinkNode {
                        link: Link {
                            id: 4,
                            source: 3,
                            target: 0,
                        },
                        children: vec![],
                    }],
                },
            ],
        };

        assert_eq!(RecursiveLinks::count_nodes(&tree), 4);
    }

    #[test]
    fn test_flatten_tree() {
        let tree = LinkNode {
            link: Link {
                id: 1,
                source: 0,
                target: 0,
            },
            children: vec![LinkNode {
                link: Link {
                    id: 2,
                    source: 1,
                    target: 0,
                },
                children: vec![],
            }],
        };

        let flattened = RecursiveLinks::flatten_tree(&tree);
        assert_eq!(flattened.len(), 2);
        assert_eq!(flattened[0].id, 1);
        assert_eq!(flattened[1].id, 2);
    }
}
