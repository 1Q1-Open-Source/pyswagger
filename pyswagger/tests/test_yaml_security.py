from __future__ import absolute_import
import os
import tempfile
import shutil
import unittest
import yaml

from pyswagger import App


class YamlSecurityTestCase(unittest.TestCase):
    """ Regression tests for YAML safety (Step 6).

    Ensures that malicious YAML tags are rejected by the project's loading path
    (which uses yaml.safe_load under the hood), while benign YAML still loads
    successfully via the existing test suite.
    """

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp(prefix="pyswagger_yaml_")

    def tearDown(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _write(self, name, content):
        p = os.path.join(self._tmpdir, name)
        with open(p, 'w') as f:
            f.write(content)
        return p

    def test_malicious_yaml_is_rejected(self):
        """App.load should fail when encountering dangerous YAML tags."""
        # Minimal Swagger 2.0 document with an extra malicious top-level key
        malicious_yaml = """
swagger: "2.0"
info:
  title: test
  version: "1.0.0"
paths: {}
x-malicious: !!python/object/apply:os.system ["echo unsafe"]
"""
        self._write('swagger.yaml', malicious_yaml)

        # Passing directory path lets LocalGetter discover swagger.yaml
        with self.assertRaises(yaml.YAMLError):
            App.load(self._tmpdir)
