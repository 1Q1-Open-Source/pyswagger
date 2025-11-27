from __future__ import absolute_import
import io
import os
import sys
import tempfile
import shutil
import unittest

from pyswagger import utils


class ImportLibLoaderTestCase(unittest.TestCase):
    """Validate dynamic import via utils.import_string (Step 1 follow-up).

    Creates a temporary module on disk, ensures it can be imported dynamically
    using the updated importlib-based loader, and verifies attributes are
    accessible and the module is present in sys.modules.
    """

    def setUp(self):
        self._tmpdir = tempfile.mkdtemp(prefix="pysw_import_")
        self._cleanup_sys_path = False

    def tearDown(self):
        # Remove path entry if we added it
        if self._cleanup_sys_path and self._tmpdir in sys.path:
            try:
                sys.path.remove(self._tmpdir)
            except ValueError:
                pass
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_dynamic_import_of_temp_module(self):
        mod_name = 'tmp_hello_mod'
        mod_code = (
            "VALUE = 42\n"
            "def greet(name):\n"
            "    return 'hello, %s' % name\n"
        )
        mod_path = os.path.join(self._tmpdir, mod_name + '.py')
        with io.open(mod_path, 'w', encoding='utf-8') as f:
            f.write(mod_code)

        # Prepend temp directory to sys.path for import
        sys.path.insert(0, self._tmpdir)
        self._cleanup_sys_path = True

        m = utils.import_string(mod_name)
        self.assertIsNotNone(m)
        self.assertIn(mod_name, sys.modules)
        self.assertTrue(hasattr(m, 'VALUE'))
        self.assertEqual(m.VALUE, 42)
        self.assertTrue(hasattr(m, 'greet'))
        self.assertEqual(m.greet('world'), 'hello, world')
