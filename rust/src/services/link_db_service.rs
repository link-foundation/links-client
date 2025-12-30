//! LinkDBService - Service wrapper for link-cli (clink) database operations

use std::env;
use std::path::PathBuf;
use std::process::Stdio;
use tokio::process::Command;
use thiserror::Error;
use tracing::{debug, error, warn};

/// Errors that can occur when using LinkDBService
#[derive(Error, Debug)]
pub enum LinkDBError {
    #[error("LinkDB not available: clink command not found. Please install link-cli.")]
    ClinkNotFound,

    #[error("LinkDB query failed: {0}")]
    QueryFailed(String),

    #[error("Failed to parse link output: {0}")]
    ParseError(String),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
}

/// A link in the database
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Link {
    /// The unique identifier of the link
    pub id: u64,
    /// The source link ID
    pub source: u64,
    /// The target link ID
    pub target: u64,
}

/// LinkDBService - Wrapper for link-cli database operations
/// Uses the clink tool (link-cli) for associative link-based data storage
pub struct LinkDBService {
    db_path: PathBuf,
    next_id: u64,
}

impl LinkDBService {
    /// Create a new LinkDBService with the specified database path
    ///
    /// # Arguments
    ///
    /// * `db_path` - Optional path to the database file. If None, uses the default path.
    pub fn new(db_path: Option<PathBuf>) -> Self {
        let default_path = PathBuf::from("data/linkdb.links");
        Self {
            db_path: db_path.unwrap_or(default_path),
            next_id: 1,
        }
    }

    /// Execute a clink command
    ///
    /// # Arguments
    ///
    /// * `query` - LiNo query string
    /// * `before` - Show state before query
    /// * `changes` - Show changes
    /// * `after` - Show state after query
    /// * `trace` - Show trace information
    pub async fn execute_query(
        &self,
        query: &str,
        before: bool,
        changes: bool,
        after: bool,
        trace: bool,
    ) -> Result<String, LinkDBError> {
        let mut args = vec![query.to_string(), "--db".to_string(), self.db_path.to_string_lossy().to_string()];

        if before {
            args.push("--before".to_string());
        }
        if changes {
            args.push("--changes".to_string());
        }
        if after {
            args.push("--after".to_string());
        }
        if trace {
            args.push("--trace".to_string());
        }

        debug!("Executing clink command: clink {}", args.join(" "));

        // Set PATH to include .dotnet/tools directory where clink is installed
        let home = env::var("HOME").unwrap_or_else(|_| String::new());
        let dotnet_tools = format!("{}/.dotnet/tools", home);
        let path = format!("{}:{}", dotnet_tools, env::var("PATH").unwrap_or_default());

        let output = Command::new("clink")
            .args(&args)
            .env("PATH", &path)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()
            .await;

        match output {
            Ok(output) => {
                if !output.status.success() {
                    let stderr = String::from_utf8_lossy(&output.stderr);
                    if stderr.contains("not found") || stderr.contains("command not found") {
                        error!("clink command not found - link-cli may not be installed");
                        return Err(LinkDBError::ClinkNotFound);
                    }
                    error!("Failed to execute clink command: {}", stderr);
                    return Err(LinkDBError::QueryFailed(stderr.to_string()));
                }

                let stderr = String::from_utf8_lossy(&output.stderr);
                if !stderr.is_empty() {
                    warn!("clink command produced stderr: {}", stderr);
                }

                Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
            }
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
                error!("clink command not found - link-cli may not be installed");
                Err(LinkDBError::ClinkNotFound)
            }
            Err(e) => {
                error!("Failed to execute clink command: {}", e);
                Err(LinkDBError::IoError(e))
            }
        }
    }

    /// Parse clink output to extract links
    /// Format: (id: source target)
    pub fn parse_links(&self, output: &str) -> Vec<Link> {
        if output.trim().is_empty() {
            return Vec::new();
        }

        let mut links = Vec::new();
        let re = regex_lite::Regex::new(r"\((\d+):\s+(\d+)\s+(\d+)\)").unwrap();

        for line in output.lines() {
            if let Some(caps) = re.captures(line.trim()) {
                if let (Some(id), Some(source), Some(target)) =
                    (caps.get(1), caps.get(2), caps.get(3))
                {
                    if let (Ok(id), Ok(source), Ok(target)) = (
                        id.as_str().parse::<u64>(),
                        source.as_str().parse::<u64>(),
                        target.as_str().parse::<u64>(),
                    ) {
                        links.push(Link { id, source, target });
                    }
                }
            }
        }

        links
    }

    /// Create a new link
    ///
    /// # Arguments
    ///
    /// * `source` - Source link ID
    /// * `target` - Target link ID
    pub async fn create_link(&self, source: u64, target: u64) -> Result<Link, LinkDBError> {
        let query = format!("() (({} {}))", source, target);
        let output = self.execute_query(&query, false, true, false, false).await?;

        let re = regex_lite::Regex::new(r"\((\d+):\s+(\d+)\s+(\d+)\)").unwrap();
        if let Some(caps) = re.captures(&output) {
            if let (Some(id), Some(src), Some(tgt)) = (caps.get(1), caps.get(2), caps.get(3)) {
                if let (Ok(id), Ok(source), Ok(target)) = (
                    id.as_str().parse::<u64>(),
                    src.as_str().parse::<u64>(),
                    tgt.as_str().parse::<u64>(),
                ) {
                    return Ok(Link { id, source, target });
                }
            }
        }

        Err(LinkDBError::ParseError("Failed to parse created link".to_string()))
    }

    /// Read all links from database
    pub async fn read_all_links(&self) -> Result<Vec<Link>, LinkDBError> {
        let query = "((($i: $s $t)) (($i: $s $t)))";
        let output = self.execute_query(query, false, false, true, false).await?;
        Ok(self.parse_links(&output))
    }

    /// Read a specific link by ID
    pub async fn read_link(&self, id: u64) -> Result<Option<Link>, LinkDBError> {
        let query = format!("((({}:$s $t)) (({}:$s $t)))", id, id);
        let output = self.execute_query(&query, false, false, true, false).await?;
        let links = self.parse_links(&output);
        Ok(links.into_iter().next())
    }

    /// Update a link
    ///
    /// # Arguments
    ///
    /// * `id` - Link ID
    /// * `new_source` - New source value
    /// * `new_target` - New target value
    pub async fn update_link(
        &self,
        id: u64,
        new_source: u64,
        new_target: u64,
    ) -> Result<Link, LinkDBError> {
        let query = format!("((({}:$s $t)) (({}: {} {})))", id, id, new_source, new_target);
        self.execute_query(&query, false, true, false, false).await?;

        Ok(Link {
            id,
            source: new_source,
            target: new_target,
        })
    }

    /// Delete a link
    pub async fn delete_link(&self, id: u64) -> Result<bool, LinkDBError> {
        let query = format!("((({}:$s $t)) ())", id);
        self.execute_query(&query, false, true, false, false).await?;
        Ok(true)
    }

    /// Store menu item data as a link
    /// This is a higher-level abstraction for storing menu items
    pub async fn store_menu_item(&mut self) -> Result<u64, LinkDBError> {
        let menu_type_id = 1000u64; // Identifier for menu items
        let item_id = self.next_id;
        self.next_id += 1;

        let link = self.create_link(item_id, menu_type_id).await?;
        Ok(link.id)
    }

    /// Get all menu items
    pub async fn get_all_menu_items(&self) -> Result<Vec<Link>, LinkDBError> {
        let all_links = self.read_all_links().await?;
        Ok(all_links.into_iter().filter(|link| link.target == 1000).collect())
    }

    /// Delete menu item
    pub async fn delete_menu_item(&self, link_id: u64) -> Result<bool, LinkDBError> {
        self.delete_link(link_id).await
    }

    /// Clear all data from database
    pub async fn clear_database(&self) -> Result<bool, LinkDBError> {
        let all_links = self.read_all_links().await?;
        for link in all_links {
            self.delete_link(link.id).await?;
        }
        Ok(true)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_links() {
        let service = LinkDBService::new(None);

        let output = "(1: 2 3)\n(4: 5 6)";
        let links = service.parse_links(output);

        assert_eq!(links.len(), 2);
        assert_eq!(links[0], Link { id: 1, source: 2, target: 3 });
        assert_eq!(links[1], Link { id: 4, source: 5, target: 6 });
    }

    #[test]
    fn test_parse_empty_output() {
        let service = LinkDBService::new(None);

        let output = "";
        let links = service.parse_links(output);

        assert!(links.is_empty());
    }
}
