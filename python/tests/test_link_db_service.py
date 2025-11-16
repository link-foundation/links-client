"""Tests for LinkDBService"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from links_client import LinkDBService


class TestLinkDBService:
    """Test LinkDBService functionality"""

    @pytest.fixture
    def service(self, tmp_path):
        """Create a LinkDBService with a temporary database"""
        db_path = tmp_path / "test.links"
        return LinkDBService(str(db_path))

    def test_parse_links(self, service):
        """Test parsing link output"""
        output = "(1: 100 200)\n(2: 300 400)"
        links = service.parse_links(output)

        assert len(links) == 2
        assert links[0] == {'id': 1, 'source': 100, 'target': 200}
        assert links[1] == {'id': 2, 'source': 300, 'target': 400}

    def test_parse_links_empty(self, service):
        """Test parsing empty output"""
        output = ""
        links = service.parse_links(output)

        assert links == []

    def test_parse_links_no_match(self, service):
        """Test parsing output with no matches"""
        output = "some random text"
        links = service.parse_links(output)

        assert links == []
