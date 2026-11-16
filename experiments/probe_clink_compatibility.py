"""Reproduce the query rejected by newer clink releases in an empty database.

Usage: python experiments/probe_clink_compatibility.py /path/to/clink
"""

from pathlib import Path
import subprocess
import sys
import tempfile

binary = sys.argv[1]
version = subprocess.run([binary, "--version"], check=True, capture_output=True, text=True, timeout=10)
print(f"clink: {version.stdout.strip()}")
with tempfile.TemporaryDirectory() as directory:
    result = subprocess.run(
        [binary, "() ((1001 1002))", "--db", str(Path(directory) / "test.links"), "--changes"],
        capture_output=True, text=True, timeout=10,
    )
    print(f"exit status: {result.returncode}")
    print(f"stdout: {result.stdout.strip()}")
    print(f"stderr: {result.stderr.strip()}")
