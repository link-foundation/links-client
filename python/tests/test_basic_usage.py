#!/usr/bin/env python3
"""
Basic test for clink (link-cli) to verify:
1. clink is installed and accessible
2. Links are created in correct format: (id: source target) WITHOUT commas
3. CRUD operations work correctly

Note: This file is designed to run as a standalone script, not as a pytest module.
The function signatures with db_path parameter are internal helpers, not pytest tests.
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Add parent directory to path to import links_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from links_client import LinkDBService


def _log(message: str, msg_type: str = 'info'):
    """Log a message with a prefix (internal helper, not a test)"""
    prefix = {
        'info': '✓',
        'error': '✗',
        'warn': '⚠',
        'test': '→'
    }.get(msg_type, '•')

    print(f"{prefix} {message}")


def _run_clink(query: str, db_path: str, flags: list = None) -> str:
    """Run a clink command directly (internal helper, not a test)"""
    if flags is None:
        flags = ['--changes']

    home = os.path.expanduser('~')
    dotnet_tools = os.path.join(home, '.dotnet', 'tools')
    env = os.environ.copy()
    env['PATH'] = f"{dotnet_tools}:{env.get('PATH', '')}"

    command = ['clink', query, '--db', db_path] + flags
    _log(f"Running: {' '.join(command)}", 'test')

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            check=True
        )

        if result.stderr:
            _log(f"stderr: {result.stderr}", 'warn')

        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"clink command failed: {error}")


def _test_clink_installation() -> bool:
    """Test if clink is installed (internal helper, not a pytest test)"""
    _log('Test 1: Verifying clink installation...', 'test')

    try:
        home = os.path.expanduser('~')
        dotnet_tools = os.path.join(home, '.dotnet', 'tools')
        env = os.environ.copy()
        env['PATH'] = f"{dotnet_tools}:{env.get('PATH', '')}"

        result = subprocess.run(
            ['clink', '--version'],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        _log(f"clink version: {result.stdout.strip()}", 'info')
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        _log('clink is not installed!', 'error')
        _log('Install with: dotnet tool install --global clink', 'info')
        return False


def _test_link_creation(db_path: str) -> bool:
    """Test creating a link (internal helper, not a pytest test)"""
    _log('Test 2: Creating a link...', 'test')

    try:
        # Create a link: (100 200)
        output = _run_clink('() ((100 200))', db_path)

        _log(f"Output: {output}", 'test')

        # Verify format: should be (id: 100 200) NOT (id: 100, 200)
        if ',' in output:
            _log('ERROR: Output contains commas! Format should be (id: source target)', 'error')
            return False

        link_match = re.search(r'\((\d+):\s+(\d+)\s+(\d+)\)', output)
        if not link_match:
            _log('ERROR: Output does not match expected format (id: source target)', 'error')
            return False

        _log(f"Created link: ({link_match.group(1)}: {link_match.group(2)} {link_match.group(3)})", 'info')
        _log('Format is CORRECT (no commas)', 'info')
        return True
    except Exception as error:
        _log(f"Link creation failed: {error}", 'error')
        return False


def _test_link_read(db_path: str) -> bool:
    """Test reading all links (internal helper, not a pytest test)"""
    _log('Test 3: Reading all links...', 'test')

    try:
        # Read all links
        output = _run_clink('((($i: $s $t)) (($i: $s $t)))', db_path, ['--after'])

        _log(f"Output: {output}", 'test')

        if not output or not output.strip():
            _log('No links found in database', 'warn')
            return False

        # Count links
        links = [line for line in output.split('\n') if re.search(r'\(\d+:\s+\d+\s+\d+\)', line)]
        _log(f"Found {len(links)} link(s)", 'info')

        return True
    except Exception as error:
        _log(f"Link read failed: {error}", 'error')
        return False


def _test_link_update(db_path: str) -> bool:
    """Test updating a link (internal helper, not a pytest test)"""
    _log('Test 4: Updating a link...', 'test')

    try:
        # First, get the first link ID
        read_output = _run_clink('((($i: $s $t)) (($i: $s $t)))', db_path, ['--after'])
        link_match = re.search(r'\((\d+):\s+\d+\s+\d+\)', read_output)

        if not link_match:
            _log('No links to update', 'warn')
            return False

        link_id = link_match.group(1)
        _log(f"Updating link {link_id}...", 'test')

        # Update: (linkId: 100 200) -> (linkId: 300 400)
        output = _run_clink(f"((({link_id}: $s $t)) (({link_id}: 300 400)))", db_path)

        _log(f"Output: {output}", 'test')

        if '300' in output and '400' in output:
            _log('Link updated successfully', 'info')
            return True
        else:
            _log('Link update result unclear', 'warn')
            return False
    except Exception as error:
        _log(f"Link update failed: {error}", 'error')
        return False


def _test_link_delete(db_path: str) -> bool:
    """Test deleting all links (internal helper, not a pytest test)"""
    _log('Test 5: Deleting all links...', 'test')

    try:
        # Delete all links: replace (any any) with nothing
        output = _run_clink('((* *)) ()', db_path)

        _log(f"Output: {output}", 'test')
        _log('All links deleted', 'info')

        # Verify deletion
        read_output = _run_clink('((($i: $s $t)) (($i: $s $t)))', db_path, ['--after'])

        if read_output and read_output.strip():
            _log('WARNING: Links still exist after deletion', 'warn')
            _log(f"Output: {read_output}", 'test')
            return False

        _log('Deletion confirmed: database is empty', 'info')
        return True
    except Exception as error:
        _log(f"Link deletion failed: {error}", 'error')
        return False


def _cleanup(db_path: str):
    """Clean up test database (internal helper, not a test)"""
    try:
        Path(db_path).unlink()
        _log('Test database cleaned up', 'info')
    except FileNotFoundError:
        # Database might not exist, that's okay
        pass


def _run_tests():
    """Run all tests (internal helper, not a pytest test)"""
    print('\n╔══════════════════════════════════════════════════════╗')
    print('║     Basic clink (link-cli) Integration Test         ║')
    print('╚══════════════════════════════════════════════════════╝\n')

    test_db = str(Path(__file__).parent / 'test.links')

    try:
        # Cleanup before tests
        _cleanup(test_db)

        # Test 1: Installation
        if not _test_clink_installation():
            raise RuntimeError('clink is not installed')

        # Test 2: Create
        if not _test_link_creation(test_db):
            raise RuntimeError('Link creation failed')

        # Test 3: Read
        if not _test_link_read(test_db):
            raise RuntimeError('Link read failed')

        # Test 4: Update
        if not _test_link_update(test_db):
            raise RuntimeError('Link update failed')

        # Test 5: Delete
        if not _test_link_delete(test_db):
            raise RuntimeError('Link deletion failed')

        print('\n╔══════════════════════════════════════════════════════╗')
        print('║              ALL TESTS PASSED ✓                      ║')
        print('╚══════════════════════════════════════════════════════╝\n')

        _log('clink is working correctly', 'info')
        _log('Links are created in correct format: (id: source target)', 'info')
        _log('NO COMMAS in link notation ✓', 'info')

        # Cleanup after tests
        _cleanup(test_db)

        return True
    except Exception as error:
        print('\n╔══════════════════════════════════════════════════════╗')
        print('║              TESTS FAILED ✗                          ║')
        print('╚══════════════════════════════════════════════════════╝\n')

        _log(f"Test suite failed: {error}", 'error')

        return False


if __name__ == '__main__':
    success = _run_tests()
    sys.exit(0 if success else 1)
