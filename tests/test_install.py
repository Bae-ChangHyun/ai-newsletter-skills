from __future__ import annotations

import unittest
from pathlib import Path

from tests.test_helpers import load_module


install = load_module("install", "install.py")


class InstallTests(unittest.TestCase):
    def test_default_ref_is_main(self):
        self.assertEqual(install.DEFAULT_REF, "main")

    def test_bootstrap_script_does_not_fallback_to_dev(self):
        script = install.bootstrap_script(Path("/tmp/home"), "owner", "repo", "main")
        self.assertNotIn("FALLBACK_REF", script)
        self.assertNotIn("fallback dev", script)
        self.assertIn('download_ref(REF)', script)


if __name__ == "__main__":
    unittest.main()
