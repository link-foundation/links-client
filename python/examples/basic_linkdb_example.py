#!/usr/bin/env python3
"""
Simple example demonstrating basic LinkDB operations.

This example shows how to:
- Create links between entities
- Read links from the database
- Update existing links
- Delete links
"""

import sys
from pathlib import Path

# Add parent directory to path to import links_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from links_client import LinkDBService


def main():
    """Demonstrate basic LinkDB operations"""
    # Create a LinkDB service with a temporary database
    db_path = Path(__file__).parent / 'example.links'
    linkdb = LinkDBService(str(db_path))

    print("=== Basic LinkDB Example ===\n")

    # Create a link between two entities
    print("1. Creating a link between entity 100 and entity 200...")
    link = linkdb.create_link(100, 200)
    print(f"   Created link: {link}\n")

    # Create another link
    print("2. Creating another link between entity 300 and entity 400...")
    link2 = linkdb.create_link(300, 400)
    print(f"   Created link: {link2}\n")

    # Read all links
    print("3. Reading all links from the database...")
    all_links = linkdb.read_all_links()
    print(f"   Found {len(all_links)} links:")
    for link in all_links:
        print(f"   - Link {link['id']}: {link['source']} -> {link['target']}")
    print()

    # Update a link
    print("4. Updating the first link to point to entity 500...")
    updated_link = linkdb.update_link(link['id'], 100, 500)
    print(f"   Updated link: {updated_link}\n")

    # Delete a link
    print("5. Deleting the second link...")
    linkdb.delete_link(link2['id'])
    print("   Link deleted\n")

    # Verify final state
    print("6. Final state of the database:")
    final_links = linkdb.read_all_links()
    print(f"   Total links: {len(final_links)}")
    for link in final_links:
        print(f"   - Link {link['id']}: {link['source']} -> {link['target']}")

    # Cleanup
    print("\nCleaning up example database...")
    db_path.unlink(missing_ok=True)
    print("Done!")


if __name__ == '__main__':
    main()
