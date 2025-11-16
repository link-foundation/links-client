#!/usr/bin/env python3
"""Example usage of MenuStorageService"""

import sys
from pathlib import Path

# Add parent directory to path to import links_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from links_client import MenuStorageService


def main():
    """Demonstrate MenuStorageService usage"""
    menu_storage = MenuStorageService()

    # Example menu structure
    menu = [
        {
            "label": "Dashboard",
            "icon": "pi pi-home",
            "to": "/dashboard",
            "items": [
                {"label": "Analytics", "to": "/dashboard/analytics"}
            ]
        },
        {
            "label": "Settings",
            "icon": "pi pi-cog",
            "to": "/settings"
        }
    ]

    print("Storing menu structure...")
    item_ids = menu_storage.store_menu_structure(menu, 0)
    print(f"Stored {len(item_ids)} menu items")

    print("\nRetrieving menu structure...")
    retrieved_menu = menu_storage.get_menu_structure(0)
    print(f"Retrieved menu: {retrieved_menu}")

    print("\nGetting statistics...")
    stats = menu_storage.get_statistics()
    print(f"Statistics: {stats}")

    print("\nClearing all menus...")
    menu_storage.clear_all_menus()
    print("Done!")


if __name__ == '__main__':
    main()
