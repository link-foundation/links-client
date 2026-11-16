"""Keep unit tests independent of clink; explicitly selected integration tests require it."""

import os
from pathlib import Path
import subprocess

import pytest


@pytest.fixture(scope="session")
def clink():
    env = os.environ.copy()
    env["PATH"] = os.pathsep.join([
        str(Path.home() / ".dotnet" / "tools"), env.get("PATH", "")
    ])
    try:
        result = subprocess.run(
            ["clink", "--version"], env=env, check=True,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as error:
        pytest.fail(f"Integration tests require clink 2.2.2: {error}")
    if result.stdout.strip().split("+")[0] != "2.2.2":
        pytest.fail(f"Integration tests require clink 2.2.2, got {result.stdout.strip()}")


@pytest.fixture(autouse=True)
def subprocess_boundary(request, monkeypatch):
    if request.node.get_closest_marker("integration"):
        request.getfixturevalue("clink")
    else:
        def unexpected_subprocess(*args, **kwargs):
            pytest.fail("Unit tests must mock subprocess.run; mark real clink tests as integration")

        monkeypatch.setattr(subprocess, "run", unexpected_subprocess)
