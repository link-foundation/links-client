"""Regression checks for Python release wiring (requires PyYAML)."""

from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class PythonReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = yaml.safe_load(
            (ROOT / ".github/workflows/python.yml").read_text()
        )["jobs"]

    def test_unit_tests_run_without_dotnet_before_integration_setup(self):
        steps = self.jobs["test-python"]["steps"]
        unit = next(i for i, step in enumerate(steps)
                    if 'pytest -m "not integration"' in step.get("run", ""))
        setup = next(i for i, step in enumerate(steps)
                     if step.get("uses", "").startswith("actions/setup-dotnet@"))
        self.assertLess(unit, setup)

    def test_integration_tests_use_compatible_clink_and_are_required(self):
        steps = self.jobs["test-python"]["steps"]
        install = next(step for step in steps
                       if "dotnet tool install" in step.get("run", ""))
        self.assertIn("clink --version 2.2.2", install["run"])
        integration = next(step for step in steps
                           if "pytest -m integration" in step.get("run", ""))
        self.assertFalse(integration.get("continue-on-error", False))
        self.assertIn("test-python", self.jobs["build"]["needs"])

    def test_built_wheel_is_imported_in_an_isolated_environment(self):
        steps = self.jobs["build"]["steps"]
        smoke = next(step for step in steps
                     if "check_python_wheel.py" in step.get("run", ""))
        self.assertIn("-m venv", smoke["run"])
        self.assertIn('bin/pip" install python/dist/*.whl', smoke["run"])

    def test_release_paths_keep_oidc_and_require_successful_tests(self):
        for name in ("auto-release", "manual-release", "publish-current"):
            with self.subTest(job=name):
                job = self.jobs[name]
                self.assertEqual(job["permissions"]["id-token"], "write")
                self.assertIn("test-python", job["needs"])
                self.assertIn("always()", job["if"])
                self.assertIn("needs.test-python.result == 'success'", job["if"])
                self.assertIn("needs.build.result == 'success'", job["if"])
                if name != "publish-current":
                    self.assertIn("github.ref == 'refs/heads/main'", job["if"])
                publish = next(step for step in job["steps"]
                               if step.get("uses", "").startswith("pypa/gh-action-pypi-publish@"))
                self.assertNotIn("password", publish.get("with", {}))
                notice = next(step for step in job["steps"]
                              if "invalid-pending-publisher" in step.get("run", ""))
                self.assertIn("failure()", notice["if"])
                self.assertIn(f"steps.{publish['id']}.outcome == 'failure'", notice["if"])
                self.assertIn("https://pypi.org/manage/project/links-client/settings/publishing/", notice["run"])
                self.assertIn("workflow: python.yml", notice["run"])

    def test_publish_current_is_explicit_and_uses_tested_artifacts_without_branch_pushes(self):
        job = self.jobs["publish-current"]
        self.assertIn("github.event_name == 'workflow_dispatch'", job["if"])
        self.assertIn("inputs.publish_current", job["if"])
        self.assertIn("!inputs.publish_current", self.jobs["manual-release"]["if"])
        steps = job["steps"]
        download = next(step for step in steps
                        if step.get("uses", "").startswith("actions/download-artifact@"))
        self.assertEqual(download["with"]["name"], "python-dist")
        commands = "\n".join(step.get("run", "") for step in steps)
        self.assertNotIn("git push", commands)
        self.assertNotIn("git commit", commands)
        self.assertIn('--target "$GITHUB_SHA"', commands)


if __name__ == "__main__":
    unittest.main()
