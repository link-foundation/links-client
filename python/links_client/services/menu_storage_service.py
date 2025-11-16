"""MenuStorageService - Service for storing menu configuration using link-cli"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from links_client.services.link_db_service import LinkDBService
from links_client.utils.logger import get_logger

logger = get_logger(__name__)

# Data directory for storing menu item content
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "menu-items"


class MenuStorageService:
    """
    MenuStorageService - Store menu configurations using link-cli

    Architecture:
    - Link-cli stores the relationships and structure (menu hierarchy)
    - File system stores the actual menu item data (JSON files)
    - Links represent parent-child relationships in menu structure

    Link schema:
    - Link (menuItemId, parentId) represents a menu item under a parent
    - Special parentId = 0 means root-level menu item
    - Link IDs are derived from content hashes for consistency
    """

    def __init__(self):
        """Initialize MenuStorageService"""
        self.link_db = LinkDBService()
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured menu items data directory exists: {DATA_DIR}")

    def generate_item_id(self, item: Dict[str, Any]) -> int:
        """
        Generate a stable ID from menu item content

        Args:
            item: Menu item

        Returns:
            Numeric ID
        """
        content = json.dumps(item, sort_keys=True)
        hash_obj = hashlib.sha256(content.encode())
        hash_hex = hash_obj.hexdigest()
        # Take first 8 characters of hash and convert to number
        return int(hash_hex[:8], 16) % 1000000  # Keep it reasonable

    def save_item_data(self, item_id: int, item: Dict[str, Any]):
        """
        Save menu item data to file

        Args:
            item_id: Item ID
            item: Menu item data
        """
        file_path = DATA_DIR / f"{item_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(item, f, indent=2)

    def load_item_data(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Load menu item data from file

        Args:
            item_id: Item ID

        Returns:
            Menu item or None if not found
        """
        file_path = DATA_DIR / f"{item_id}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def store_menu_item(self, item: Dict[str, Any], parent_id: int = 0) -> int:
        """
        Store a menu item with its parent relationship

        Args:
            item: Menu item (must have label, icon, to/items)
            parent_id: Parent item ID (0 for root)

        Returns:
            Item ID
        """
        item_id = self.generate_item_id(item)

        # Save item data to file
        self.save_item_data(item_id, item)

        # Create link in database: (itemId, parentId)
        try:
            self.link_db.create_link(item_id, parent_id)
            logger.info(f"Menu item stored in link database: itemId={item_id}, parentId={parent_id}")
        except Exception as error:
            # Link might already exist, that's okay
            logger.debug(f"Link already exists or failed to create: itemId={item_id}, parentId={parent_id}")

        return item_id

    def store_menu_structure(self, menu_items: List[Dict[str, Any]], parent_id: int = 0) -> List[int]:
        """
        Store a complete menu structure recursively

        Args:
            menu_items: Menu items array
            parent_id: Parent ID

        Returns:
            List of created item IDs
        """
        item_ids = []

        for item in menu_items:
            # Create a copy without nested items for the link
            item_without_children = {k: v for k, v in item.items() if k != 'items'}
            children = item.get('items', [])

            # Store the item
            item_id = self.store_menu_item(item_without_children, parent_id)
            item_ids.append(item_id)

            # Recursively store children
            if children and isinstance(children, list) and len(children) > 0:
                self.store_menu_structure(children, item_id)

        return item_ids

    def get_menu_structure(self, parent_id: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve menu structure by building from links

        Args:
            parent_id: Parent ID (0 for root)

        Returns:
            List of menu items
        """
        # Get all links from database
        all_links = self.link_db.read_all_links()

        # Filter links that have this parent
        child_links = [link for link in all_links if link['target'] == parent_id]

        # Build menu items
        menu_items = []

        for link in child_links:
            item_id = link['source']

            # Load item data
            item_data = self.load_item_data(item_id)

            if item_data:
                # Recursively get children
                children = self.get_menu_structure(item_id)

                menu_item = {
                    **item_data,
                    '_linkId': link['id'],
                    '_itemId': item_id
                }

                # Add children if any
                if children:
                    menu_item['items'] = children

                menu_items.append(menu_item)

        return menu_items

    def get_all_menu_items(self) -> List[Dict[str, Any]]:
        """
        Get all menu items (flat list)

        Returns:
            List of all menu items
        """
        all_links = self.link_db.read_all_links()
        items = []

        for link in all_links:
            item_data = self.load_item_data(link['source'])
            if item_data:
                items.append({
                    **item_data,
                    '_linkId': link['id'],
                    '_itemId': link['source'],
                    '_parentId': link['target']
                })

        return items

    def delete_menu_item(self, item_id: int) -> bool:
        """
        Delete a menu item and its children

        Args:
            item_id: Item ID

        Returns:
            Success status
        """
        # Get all child items
        children = self.get_menu_structure(item_id)

        # Recursively delete children
        for child in children:
            self.delete_menu_item(child['_itemId'])

        # Delete links where this item is the source
        all_links = self.link_db.read_all_links()
        item_links = [link for link in all_links if link['source'] == item_id]

        for link in item_links:
            self.link_db.delete_link(link['id'])

        # Delete item data file
        try:
            file_path = DATA_DIR / f"{item_id}.json"
            file_path.unlink()
        except Exception as error:
            logger.warning(f"Failed to delete item data file: itemId={item_id}, error={error}")

        return True

    def clear_all_menus(self) -> bool:
        """
        Clear all menu data

        Returns:
            Success status
        """
        # Clear link database
        self.link_db.clear_database()

        # Clear all menu item files
        try:
            for file_path in DATA_DIR.glob("*.json"):
                file_path.unlink()
        except Exception as error:
            logger.warning(f"Failed to clear menu data files: {error}")

        return True

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about stored menu data

        Returns:
            Statistics dictionary
        """
        all_links = self.link_db.read_all_links()
        json_files = list(DATA_DIR.glob("*.json"))

        return {
            'totalLinks': len(all_links),
            'totalFiles': len(json_files),
            'rootItems': len([link for link in all_links if link['target'] == 0])
        }
