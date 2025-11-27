"""
Legacy notice: The webapp2 client was Python 2–only and has been removed for Python 3.10+.

This module intentionally provides only a stub to alert callers that the legacy
client is no longer available. If you still need a similar in-process client for
tests, consider using the Flask client or requests-based client.
"""

from ...core import BaseClient


class Webapp2TestClient(BaseClient):
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            'The legacy webapp2 client was removed (Python 2-only). '
            'Use a supported client (e.g., requests, flask) or pin an older revision.'
        )

