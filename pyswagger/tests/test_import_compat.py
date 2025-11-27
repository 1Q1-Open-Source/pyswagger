from __future__ import absolute_import
import unittest
from collections.abc import MutableMapping


class ImportCompatTestCase(unittest.TestCase):
    """Smoke tests for imports on modern Python (collections.abc, importlib).

    Verifies that modules updated in Step 1 import without errors and expose
    expected symbols across Python 3.8/3.10/3.12.
    """

    def test_import_modules(self):
        # Should import cleanly on all supported Python versions
        import pyswagger.io as io_mod
        import pyswagger.utils as utils_mod

        # Basic sanity on expected attributes/functions
        self.assertTrue(hasattr(io_mod, 'Request'))
        self.assertTrue(hasattr(utils_mod, 'import_string'))

        # CaseInsensitiveDict should be a MutableMapping from collections.abc
        self.assertTrue(hasattr(utils_mod, 'CaseInsensitiveDict'))
        self.assertTrue(issubclass(utils_mod.CaseInsensitiveDict, MutableMapping))
