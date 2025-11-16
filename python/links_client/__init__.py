"""
Links Client - Python client library for link-cli (Links Theory database)

This package provides a Python interface to the link-cli (clink) tool for
working with Links Theory databases.
"""

from links_client.services.link_db_service import LinkDBService
from links_client.services.menu_storage_service import MenuStorageService
from links_client.services.auth_storage_service import AuthStorageService

__version__ = "1.0.0"
__all__ = ["LinkDBService", "MenuStorageService", "AuthStorageService"]
