#!/usr/bin/env python3
"""Example usage of AuthStorageService"""

import sys
from pathlib import Path

# Add parent directory to path to import links_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from links_client import AuthStorageService


def main():
    """Demonstrate AuthStorageService usage"""
    auth_storage = AuthStorageService()

    # Create a user
    print("Creating user...")
    user = auth_storage.create_user({
        "username": "alice",
        "email": "alice@example.com"
    })
    print(f"Created user: {user}")

    user_id = user['userId']

    # Set password
    print("\nSetting password...")
    password = auth_storage.set_password(user_id, {
        "hash": "hashed_password_here",
        "salt": "random_salt_here"
    })
    print(f"Password set: {password['passwordId']}")

    # Create a token
    print("\nCreating token...")
    token = auth_storage.create_token(user_id, {
        "apiKey": "api_key_12345",
        "permissions": ["read", "write"]
    })
    print(f"Created token: {token}")

    # Get user
    print("\nRetrieving user...")
    retrieved_user = auth_storage.get_user(user_id)
    print(f"Retrieved user: {retrieved_user}")

    # Get statistics
    print("\nGetting statistics...")
    stats = auth_storage.get_statistics()
    print(f"Statistics: {stats}")

    # Cleanup
    print("\nCleaning up...")
    auth_storage.clear_all_auth_data()
    print("Done!")


if __name__ == '__main__':
    main()
