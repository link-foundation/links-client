"""Tests for LinkDBService"""

import pytest
import logging
import subprocess
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

    def test_execute_query_flags_and_output(self, service, monkeypatch):
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0, "  (1: 2 3)\n", "")

        monkeypatch.setattr(subprocess, "run", run)
        assert service.execute_query(
            "() ((2 3))", before=True, changes=True, after=True, trace=True
        ) == "(1: 2 3)"
        command, kwargs = calls[0]
        assert command == [
            "clink", "() ((2 3))", "--db", service.db_path,
            "--before", "--changes", "--after", "--trace",
        ]
        assert kwargs["check"] is True
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True

    def test_execute_query_missing_binary(self, service, monkeypatch):
        def run(*args, **kwargs):
            raise FileNotFoundError("clink")

        monkeypatch.setattr(subprocess, "run", run)
        with pytest.raises(RuntimeError, match="clink command not found"):
            service.execute_query("() ((1 2))")

    def test_execute_query_failure_preserves_debug_diagnostics(self, service, monkeypatch, caplog):
        def run(command, **kwargs):
            raise subprocess.CalledProcessError(
                1, command, output="query output", stderr="missing reference 1001"
            )

        monkeypatch.setattr(subprocess, "run", run)
        with caplog.at_level(logging.DEBUG, logger="links_client.services.link_db_service"):
            with pytest.raises(RuntimeError, match="LinkDB query failed"):
                service.execute_query("() ((1001 1002))", changes=True)
        assert "missing reference 1001" in caplog.text
        assert "query output" in caplog.text

    def test_create_link_uses_changes_output(self, service, monkeypatch):
        def execute(query, **kwargs):
            assert query == "() ((1001 1002))"
            assert kwargs == {"changes": True}
            return "()\n(1: 1001 1002)"

        monkeypatch.setattr(service, "execute_query", execute)
        assert service.create_link(1001, 1002) == {
            "id": 1, "source": 1001, "target": 1002
        }
