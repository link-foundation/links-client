"""Regression checks for Rust registry releases (requires PyYAML)."""

from pathlib import Path
import os
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


class RustReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = yaml.safe_load(
            (ROOT / ".github/workflows/rust.yml").read_text()
        )["jobs"]

    def test_release_paths_publish_before_creating_github_release(self):
        for job_name in ("auto-release", "manual-release"):
            with self.subTest(job=job_name):
                job = self.jobs[job_name]
                self.assertIn("github.ref == 'refs/heads/main'", job["if"])
                self.assertEqual(job["permissions"].get("id-token"), "write")
                steps = job["steps"]
                publish = [
                    step for step in steps
                    if step.get("run") == "bash scripts/publish.sh"
                ]
                self.assertEqual(len(publish), 1, "Release must upload to crates.io")
                publish = publish[0]
                self.assertEqual(publish["working-directory"], "./rust")
                auth = [
                    step for step in steps
                    if step.get("uses", "").startswith("rust-lang/crates-io-auth-action@")
                ]
                self.assertEqual(len(auth), 1)
                auth = auth[0]
                self.assertRegex(auth["uses"], r"@[0-9a-f]{40}$")
                self.assertIs(auth.get("continue-on-error"), True)
                self.assertEqual(
                    publish["env"]["CARGO_REGISTRY_TOKEN"],
                    "${{ steps." + auth["id"] + ".outputs.token || "
                    "secrets.CARGO_REGISTRY_TOKEN || secrets.CARGO_TOKEN }}",
                )
                self.assertEqual(auth.get("if"), publish.get("if"))
                release = next(
                    step for step in steps if "gh release create" in step.get("run", "")
                )
                self.assertLess(steps.index(auth), steps.index(publish))
                self.assertLess(steps.index(publish), steps.index(release))
                self.assertFalse(publish.get("continue-on-error", False))
                self.assertEqual(publish.get("if"), release.get("if"))

    def test_pr_build_verifies_the_publishable_package_without_credentials(self):
        steps = self.jobs["build"]["steps"]
        dry_run = [step for step in steps if "cargo publish --dry-run" in step.get("run", "")]
        self.assertEqual(len(dry_run), 1)
        self.assertIn("--locked", dry_run[0]["run"])
        self.assertNotIn("CARGO_REGISTRY_TOKEN", dry_run[0].get("env", {}))


class PublishScriptTests(unittest.TestCase):
    def run_publish(self, status, token="test-token", publish_exit=0, curl_exit=0):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            cargo = work / "cargo"
            cargo.write_text(
                '#!/bin/sh\nif [ "$1" = metadata ]; then\n'
                'echo \'{"packages":[{"name":"links-client","version":"1.0.0"}]}\'\n'
                'else\nprintf "%s\\n" "$*" > "$CALL_LOG"\n'
                'exit "$PUBLISH_EXIT"\nfi\n'
            )
            curl = work / "curl"
            curl.write_text('#!/bin/sh\nprintf "%s" "$HTTP_STATUS"\nexit "$CURL_EXIT"\n')
            cargo.chmod(0o755)
            curl.chmod(0o755)
            log = work / "calls"
            env = dict(
                os.environ,
                PATH=f"{work}:{os.environ['PATH']}",
                HTTP_STATUS=status,
                CARGO_REGISTRY_TOKEN=token,
                CALL_LOG=str(log),
                PUBLISH_EXIT=str(publish_exit),
                CURL_EXIT=str(curl_exit),
            )
            result = subprocess.run(
                ["bash", str(ROOT / "rust/scripts/publish.sh")],
                cwd=work, env=env, text=True, capture_output=True, timeout=10,
            )
            self.assertNotIn("test-token", result.stdout + result.stderr)
            return result, log.read_text().strip() if log.exists() else None

    def test_missing_version_is_published_with_locked_dependencies(self):
        result, call = self.run_publish("404")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(call, "publish --locked")

    def test_existing_version_allows_release_recovery_without_credentials(self):
        result, call = self.run_publish("200", token="")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(call)

    def test_missing_credentials_fail_with_setup_instructions(self):
        result, call = self.run_publish("404", token="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("trusted publisher", result.stdout)
        self.assertIsNone(call)

    def test_registry_errors_do_not_upload(self):
        for status, curl_exit in (("500", 0), ("403", 0), ("000", 7)):
            with self.subTest(status=status):
                result, call = self.run_publish(status, curl_exit=curl_exit)
                self.assertNotEqual(result.returncode, 0)
                self.assertIsNone(call)

    def test_publish_failure_is_not_hidden(self):
        result, call = self.run_publish("404", publish_exit=42)
        self.assertEqual(result.returncode, 42)
        self.assertEqual(call, "publish --locked")


if __name__ == "__main__":
    unittest.main()
