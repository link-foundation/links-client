"""LinkDBService - Service wrapper for link-cli (clink) database operations"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
from links_client.utils.logger import get_logger

logger = get_logger(__name__)

# Default database path
DEFAULT_DB_DIR = Path(__file__).parent.parent.parent.parent / "data"
DEFAULT_DB_FILE = DEFAULT_DB_DIR / "linkdb.links"


class LinkDBService:
    """
    LinkDBService - Wrapper for link-cli database operations
    Uses the clink tool (link-cli) for associative link-based data storage
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize LinkDBService

        Args:
            db_path: Path to database file (defaults to DEFAULT_DB_FILE)
        """
        self.db_path = db_path or str(DEFAULT_DB_FILE)
        self.next_id = 1  # Track next available ID for menu items

    def execute_query(
        self,
        query: str,
        before: bool = False,
        changes: bool = False,
        after: bool = False,
        trace: bool = False
    ) -> str:
        """
        Execute a clink command

        Args:
            query: LiNo query string
            before: Show state before query
            changes: Show changes
            after: Show state after query
            trace: Show trace information

        Returns:
            Command output

        Raises:
            RuntimeError: If clink is not available or query fails
        """
        flags = []
        if before:
            flags.append('--before')
        if changes:
            flags.append('--changes')
        if after:
            flags.append('--after')
        if trace:
            flags.append('--trace')

        command = ['clink', query, '--db', self.db_path] + flags

        try:
            logger.debug(f"Executing clink command: {' '.join(command)}")

            # Set PATH to include .dotnet/tools directory where clink is installed
            env = os.environ.copy()
            home = os.path.expanduser('~')
            dotnet_tools = os.path.join(home, '.dotnet', 'tools')
            env['PATH'] = f"{dotnet_tools}:{env.get('PATH', '')}"

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=env,
                check=True
            )

            if result.stderr:
                logger.warning(f"clink command produced stderr: {result.stderr}")

            return result.stdout.strip()

        except FileNotFoundError:
            logger.error("clink command not found - link-cli may not be installed")
            raise RuntimeError(
                "LinkDB not available: clink command not found. "
                "Please install link-cli."
            )
        except subprocess.CalledProcessError as error:
            logger.error(f"Failed to execute clink command: {error}")
            raise RuntimeError(f"LinkDB query failed: {error}")

    def parse_links(self, output: str) -> List[Dict[str, int]]:
        """
        Parse clink output to extract links
        Format: (id: source target)

        Args:
            output: Raw clink output

        Returns:
            List of parsed links
        """
        if not output or not output.strip():
            return []

        lines = [line.strip() for line in output.split('\n') if line.strip()]
        links = []

        for line in lines:
            # Match pattern: (id: source target)
            match = re.match(r'\((\d+):\s+(\d+)\s+(\d+)\)', line)
            if match:
                links.append({
                    'id': int(match.group(1)),
                    'source': int(match.group(2)),
                    'target': int(match.group(3))
                })

        return links

    def create_link(self, source: int, target: int) -> Dict[str, int]:
        """
        Create a new link

        Args:
            source: Source link ID
            target: Target link ID

        Returns:
            Created link

        Raises:
            RuntimeError: If link creation fails
        """
        query = f"() (({source} {target}))"
        output = self.execute_query(query, changes=True)

        # Parse the created link from output
        match = re.search(r'\((\d+):\s+(\d+)\s+(\d+)\)', output)
        if match:
            return {
                'id': int(match.group(1)),
                'source': int(match.group(2)),
                'target': int(match.group(3))
            }

        raise RuntimeError("Failed to parse created link")

    def read_all_links(self) -> List[Dict[str, int]]:
        """
        Read all links from database

        Returns:
            List of all links
        """
        query = "((($i: $s $t)) (($i: $s $t)))"
        output = self.execute_query(query, after=True)
        return self.parse_links(output)

    def read_link(self, link_id: int) -> Optional[Dict[str, int]]:
        """
        Read a specific link by ID

        Args:
            link_id: Link ID

        Returns:
            Link or None if not found
        """
        query = f"((({link_id}: $s $t)) (({link_id}: $s $t)))"
        output = self.execute_query(query, after=True)
        links = self.parse_links(output)
        return links[0] if links else None

    def update_link(self, link_id: int, new_source: int, new_target: int) -> Dict[str, int]:
        """
        Update a link

        Args:
            link_id: Link ID
            new_source: New source value
            new_target: New target value

        Returns:
            Updated link
        """
        query = f"((({link_id}: $s $t)) (({link_id}: {new_source} {new_target})))"
        self.execute_query(query, changes=True)

        return {
            'id': link_id,
            'source': new_source,
            'target': new_target
        }

    def delete_link(self, link_id: int) -> bool:
        """
        Delete a link

        Args:
            link_id: Link ID

        Returns:
            Success status
        """
        query = f"((({link_id}: $s $t)) ())"
        self.execute_query(query, changes=True)
        return True

    def store_menu_item(self, menu_item: Dict[str, Any]) -> int:
        """
        Store menu item data as a link with encoded JSON
        This is a higher-level abstraction for storing menu items

        Args:
            menu_item: Menu item object

        Returns:
            Link ID
        """
        # For now, we'll store the menu item as a link where:
        # - source = incrementing ID
        # - target = menu type identifier

        menu_type_id = 1000  # Identifier for menu items
        item_id = self.next_id
        self.next_id += 1

        link = self.create_link(item_id, menu_type_id)

        # Store the actual JSON data separately (we'll need to implement a string storage mechanism)
        # For now, return the link ID
        return link['id']

    def get_all_menu_items(self) -> List[Dict[str, int]]:
        """
        Get all menu items

        Returns:
            List of menu items
        """
        # Read all links with source pointing to menu type
        all_links = self.read_all_links()

        # Filter links that represent menu items (target = 1000)
        menu_links = [link for link in all_links if link['target'] == 1000]

        return menu_links

    def delete_menu_item(self, link_id: int) -> bool:
        """
        Delete menu item

        Args:
            link_id: Link ID

        Returns:
            Success status
        """
        return self.delete_link(link_id)

    def clear_database(self) -> bool:
        """
        Clear all data from database

        Returns:
            Success status
        """
        try:
            # Delete all links one by one
            all_links = self.read_all_links()
            for link in all_links:
                self.delete_link(link['id'])
            return True
        except Exception as error:
            logger.error(f"Failed to clear database: {error}")
            raise
