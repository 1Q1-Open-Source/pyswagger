import unittest

# The legacy webapp2 client was Python 2-only and has been removed.
# Skip this entire module at import time so both unittest and pytest
# will ignore it without requiring pytest to be installed.
raise unittest.SkipTest(
    "Skipping legacy webapp2 tests: the webapp2 client was removed (Python 2-only)"
)

# Intentionally left blank; module retained to preserve historical path.

