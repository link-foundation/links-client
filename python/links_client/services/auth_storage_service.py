"""AuthStorageService - Service for storing authentication data using link-cli"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from links_client.services.link_db_service import LinkDBService
from links_client.utils.logger import get_logger

logger = get_logger(__name__)

# Data directories for storing authentication data
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "auth-data"
USERS_DIR = DATA_DIR / "users"
TOKENS_DIR = DATA_DIR / "tokens"
PASSWORDS_DIR = DATA_DIR / "passwords"
AUTH_DB_FILE = DATA_DIR / "auth.links"

# Type identifiers for links
USER_TYPE_ID = 2000  # Links of type (userId 2000) represent users
TOKEN_LINK_PARENT = 3000  # Parent for token links (tokenId userId)
PASSWORD_LINK_PARENT = 4000  # Parent for password links (passwordId userId)


class AuthStorageService:
    """
    AuthStorageService - Store authentication data using link-cli

    Architecture:
    - Link-cli stores relationships between entities
    - File system stores the actual data (JSON files)
    - Links represent entity types and relationships

    Link schemas:
    1. Users: (userId 2000) - represents a user entity
    2. Tokens: (tokenId userId) - token belongs to user
    3. Passwords: (passwordId userId) - password belongs to user

    File storage:
    - data/auth-data/users/{userId}.json - user profile data
    - data/auth-data/tokens/{tokenId}.json - token data
    - data/auth-data/passwords/{passwordId}.json - hashed password data
    """

    def __init__(self):
        """Initialize AuthStorageService"""
        self.link_db = LinkDBService(str(AUTH_DB_FILE))
        self._ensure_data_directories()

    def _ensure_data_directories(self):
        """Ensure all data directories exist"""
        for directory in [DATA_DIR, USERS_DIR, TOKENS_DIR, PASSWORDS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured auth data directory exists: {directory}")

    def generate_id(self, content: Dict[str, Any], prefix: str = '') -> str:
        """
        Generate a stable ID from content

        Args:
            content: Content object
            prefix: ID prefix (e.g., 'user', 'token', 'pwd')

        Returns:
            Unique ID
        """
        content_str = json.dumps(content, sort_keys=True) + str(time.time())
        hash_obj = hashlib.sha256(content_str.encode())
        hash_hex = hash_obj.hexdigest()
        numeric_id = int(hash_hex[:12], 16)
        return f"{prefix}_{numeric_id}" if prefix else str(numeric_id)

    def id_to_number(self, id_str: str) -> int:
        """
        Convert string ID to numeric for link storage

        Args:
            id_str: String ID

        Returns:
            Numeric ID
        """
        hash_obj = hashlib.sha256(id_str.encode())
        hash_hex = hash_obj.hexdigest()
        return int(hash_hex[:8], 16) % 1000000000

    def save_data(self, directory: Path, item_id: str, data: Dict[str, Any]):
        """
        Save data to file

        Args:
            directory: Directory path
            item_id: Item ID
            data: Data to save
        """
        file_path = directory / f"{item_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_data(self, directory: Path, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Load data from file

        Args:
            directory: Directory path
            item_id: Item ID

        Returns:
            Data or None if not found
        """
        file_path = directory / f"{item_id}.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    # ==================== USER OPERATIONS ====================

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user

        Args:
            user_data: User data (username, email, profile, etc.)

        Returns:
            Created user with ID
        """
        user_id = self.generate_id(user_data, 'user')
        user_id_numeric = self.id_to_number(user_id)

        # Save user data to file
        user_data_with_id = {
            **user_data,
            'userId': user_id,
            'createdAt': datetime.utcnow().isoformat()
        }
        self.save_data(USERS_DIR, user_id, user_data_with_id)

        # Create link: (userId, USER_TYPE_ID)
        try:
            self.link_db.create_link(user_id_numeric, USER_TYPE_ID)
            logger.info(f"User created in link database: {user_id}")
        except Exception as error:
            logger.error(f"Failed to create user link: {user_id}, error: {error}")
            raise

        return user_data_with_id

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID

        Args:
            user_id: User ID

        Returns:
            User data or None
        """
        return self.load_data(USERS_DIR, user_id)

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users

        Returns:
            List of users
        """
        users = []
        try:
            for file_path in USERS_DIR.glob("*.json"):
                user_data = self.load_data(USERS_DIR, file_path.stem)
                if user_data:
                    users.append(user_data)
        except Exception as error:
            logger.warning(f"Error reading users directory: {error}")

        return users

    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user data

        Args:
            user_id: User ID
            updates: Data to update

        Returns:
            Updated user data
        """
        existing_user = self.get_user(user_id)
        if not existing_user:
            raise ValueError(f"User {user_id} not found")

        updated_user = {
            **existing_user,
            **updates,
            'userId': user_id,  # Preserve userId
            'updatedAt': datetime.utcnow().isoformat()
        }

        self.save_data(USERS_DIR, user_id, updated_user)
        logger.info(f"User updated: {user_id}")

        return updated_user

    def delete_user(self, user_id: str) -> bool:
        """
        Delete user and all associated data (tokens, passwords)

        Args:
            user_id: User ID

        Returns:
            Success status
        """
        user_id_numeric = self.id_to_number(user_id)

        # Delete user's tokens
        user_tokens = self.get_user_tokens(user_id)
        for token in user_tokens:
            self.delete_token(token['tokenId'])

        # Delete user's passwords
        user_passwords = self.get_user_passwords(user_id)
        for pwd in user_passwords:
            self.delete_password(pwd['passwordId'])

        # Delete user link
        all_links = self.link_db.read_all_links()
        user_link = next(
            (link for link in all_links
             if link['source'] == user_id_numeric and link['target'] == USER_TYPE_ID),
            None
        )

        if user_link:
            self.link_db.delete_link(user_link['id'])

        # Delete user data file
        try:
            file_path = USERS_DIR / f"{user_id}.json"
            file_path.unlink()
            logger.info(f"User deleted: {user_id}")
        except Exception as error:
            logger.warning(f"Failed to delete user data file: {user_id}, error: {error}")

        return True

    # ==================== TOKEN OPERATIONS ====================

    def create_token(self, user_id: str, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new token for a user

        Args:
            user_id: User ID
            token_data: Token data (apiKey, permissions, expiresAt, etc.)

        Returns:
            Created token with ID
        """
        token_id = self.generate_id(token_data, 'token')
        token_id_numeric = self.id_to_number(token_id)
        user_id_numeric = self.id_to_number(user_id)

        # Save token data to file
        token_data_with_id = {
            **token_data,
            'tokenId': token_id,
            'userId': user_id,
            'createdAt': datetime.utcnow().isoformat()
        }
        self.save_data(TOKENS_DIR, token_id, token_data_with_id)

        # Create link: (tokenId, userId)
        try:
            self.link_db.create_link(token_id_numeric, user_id_numeric)
            logger.info(f"Token created in link database: tokenId={token_id}, userId={user_id}")
        except Exception as error:
            logger.error(f"Failed to create token link: tokenId={token_id}, userId={user_id}, error: {error}")
            raise

        return token_data_with_id

    def get_token(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        Get token by ID

        Args:
            token_id: Token ID

        Returns:
            Token data or None
        """
        return self.load_data(TOKENS_DIR, token_id)

    def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all tokens for a user

        Args:
            user_id: User ID

        Returns:
            List of tokens
        """
        tokens = []
        try:
            for file_path in TOKENS_DIR.glob("*.json"):
                token_data = self.load_data(TOKENS_DIR, file_path.stem)
                if token_data and token_data.get('userId') == user_id:
                    tokens.append(token_data)
        except Exception as error:
            logger.warning(f"Error reading tokens directory: {error}")

        return tokens

    def delete_token(self, token_id: str) -> bool:
        """
        Delete a token

        Args:
            token_id: Token ID

        Returns:
            Success status
        """
        token_id_numeric = self.id_to_number(token_id)

        # Delete token link
        all_links = self.link_db.read_all_links()
        token_link = next(
            (link for link in all_links if link['source'] == token_id_numeric),
            None
        )

        if token_link:
            self.link_db.delete_link(token_link['id'])

        # Delete token data file
        try:
            file_path = TOKENS_DIR / f"{token_id}.json"
            file_path.unlink()
            logger.info(f"Token deleted: {token_id}")
        except Exception as error:
            logger.warning(f"Failed to delete token data file: {token_id}, error: {error}")

        return True

    # ==================== PASSWORD OPERATIONS ====================

    def set_password(self, user_id: str, password_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create/update password for a user

        Args:
            user_id: User ID
            password_data: Password data (hash, salt, algorithm)

        Returns:
            Created/updated password with ID
        """
        # First, delete existing passwords for this user
        existing_passwords = self.get_user_passwords(user_id)
        for pwd in existing_passwords:
            self.delete_password(pwd['passwordId'])

        # Create new password
        password_id = self.generate_id(password_data, 'pwd')
        password_id_numeric = self.id_to_number(password_id)
        user_id_numeric = self.id_to_number(user_id)

        # Save password data to file
        password_data_with_id = {
            **password_data,
            'passwordId': password_id,
            'userId': user_id,
            'createdAt': datetime.utcnow().isoformat()
        }
        self.save_data(PASSWORDS_DIR, password_id, password_data_with_id)

        # Create link: (passwordId, userId)
        try:
            self.link_db.create_link(password_id_numeric, user_id_numeric)
            logger.info(f"Password created in link database: passwordId={password_id}, userId={user_id}")
        except Exception as error:
            logger.error(f"Failed to create password link: passwordId={password_id}, userId={user_id}, error: {error}")
            raise

        return password_data_with_id

    def get_user_password(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get password for a user

        Args:
            user_id: User ID

        Returns:
            Password data or None
        """
        passwords = self.get_user_passwords(user_id)
        # Return the most recent password (should only be one)
        return passwords[0] if passwords else None

    def get_user_passwords(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all passwords for a user (for migration/history)

        Args:
            user_id: User ID

        Returns:
            List of passwords
        """
        passwords = []
        try:
            for file_path in PASSWORDS_DIR.glob("*.json"):
                password_data = self.load_data(PASSWORDS_DIR, file_path.stem)
                if password_data and password_data.get('userId') == user_id:
                    passwords.append(password_data)
        except Exception as error:
            logger.warning(f"Error reading passwords directory: {error}")

        return passwords

    def delete_password(self, password_id: str) -> bool:
        """
        Delete a password

        Args:
            password_id: Password ID

        Returns:
            Success status
        """
        password_id_numeric = self.id_to_number(password_id)

        # Delete password link
        all_links = self.link_db.read_all_links()
        password_link = next(
            (link for link in all_links if link['source'] == password_id_numeric),
            None
        )

        if password_link:
            self.link_db.delete_link(password_link['id'])

        # Delete password data file
        try:
            file_path = PASSWORDS_DIR / f"{password_id}.json"
            file_path.unlink()
            logger.info(f"Password deleted: {password_id}")
        except Exception as error:
            logger.warning(f"Failed to delete password data file: {password_id}, error: {error}")

        return True

    # ==================== STATISTICS & UTILITIES ====================

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored authentication data

        Returns:
            Statistics dictionary
        """
        all_links = self.link_db.read_all_links()

        user_files = list(USERS_DIR.glob("*.json"))
        token_files = list(TOKENS_DIR.glob("*.json"))
        password_files = list(PASSWORDS_DIR.glob("*.json"))

        return {
            'totalLinks': len(all_links),
            'users': {
                'links': len([link for link in all_links if link['target'] == USER_TYPE_ID]),
                'files': len(user_files)
            },
            'tokens': {
                'links': len([link for link in all_links
                            if link['target'] != USER_TYPE_ID and link['target'] < 1000000000]),
                'files': len(token_files)
            },
            'passwords': {
                'files': len(password_files)
            }
        }

    def clear_all_auth_data(self) -> bool:
        """
        Clear all authentication data (DANGEROUS - use with caution)

        Returns:
            Success status
        """
        logger.warning("Clearing ALL authentication data - this is irreversible!")

        # Clear link database
        self.link_db.clear_database()

        # Clear all data files
        for directory in [USERS_DIR, TOKENS_DIR, PASSWORDS_DIR]:
            try:
                for file_path in directory.glob("*.json"):
                    file_path.unlink()
                logger.info(f"Cleared auth data directory: {directory}")
            except Exception as error:
                logger.warning(f"Failed to clear auth data directory: {directory}, error: {error}")

        return True

    def find_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Find user by username (requires scanning all users)

        Args:
            username: Username to search for

        Returns:
            User data or None
        """
        all_users = self.get_all_users()
        return next((user for user in all_users if user.get('username') == username), None)

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find user by email (requires scanning all users)

        Args:
            email: Email to search for

        Returns:
            User data or None
        """
        all_users = self.get_all_users()
        return next((user for user in all_users if user.get('email') == email), None)

    def find_token_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Find token by API key (requires scanning all tokens)

        Args:
            api_key: API key to search for

        Returns:
            Token data or None
        """
        try:
            for file_path in TOKENS_DIR.glob("*.json"):
                token_data = self.load_data(TOKENS_DIR, file_path.stem)
                if token_data and token_data.get('apiKey') == api_key:
                    return token_data
        except Exception as error:
            logger.warning(f"Error searching for token by API key: {error}")

        return None
