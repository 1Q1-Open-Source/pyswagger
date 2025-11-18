from __future__ import absolute_import
from pyswagger.primitives import MimeCodec
import unittest


class CodecTestCase(unittest.TestCase):
    def test_register_unregister(self):
        mime_codec = MimeCodec()
        mime = 'test'
        dummy_codec = {}
        self.assertEqual(None, mime_codec.codec(mime))
        mime_codec.register(mime, dummy_codec)
        self.assertEqual(dummy_codec, mime_codec.codec(mime))
        mime_codec.unregister(mime)
        self.assertEqual(None, mime_codec.codec(mime))

    def test_plain_codec(self):
        mime_codec = MimeCodec()
        mime = 'text/plain'
        text = 'plain text'
        self.assertEqual(text, mime_codec.marshal(mime, text))
        self.assertEqual(text, mime_codec.unmarshal(mime, text))

    def test_json_codec(self):
        mime_codec = MimeCodec()
        mime = 'application/json'
        value = dict(key='value')
        data = '{"key": "value"}'
        self.assertEqual(data, mime_codec.marshal(mime, value))
        self.assertEqual(value, mime_codec.unmarshal(mime, data))

    def test_hal_json_codec(self):
        mime_codec = MimeCodec()
        value = {
            '_links': {
                'self': {'href': '/orders'},
                'next': {'href': '/orders?page=2'}
            },
            '_embedded': {
                'orders': [
                    {'id': 1, 'status': 'shipped'},
                    {'id': 2, 'status': 'processing'}
                ]
            },
            'count': 2
        }
        # application/hal+json should reuse JSON semantics
        mime = 'application/hal+json'
        data = '{"_links": {"self": {"href": "/orders"}, "next": {"href": "/orders?page=2"}}, "_embedded": {"orders": [{"id": 1, "status": "shipped"}, {"id": 2, "status": "processing"}]}, "count": 2}'
        self.assertEqual(data, mime_codec.marshal(mime, value))
        self.assertEqual(value, mime_codec.unmarshal(mime, data))

        # parameterized content type should still match
        mime_with_charset = 'application/hal+json; charset=utf-8'
        self.assertEqual(data, mime_codec.marshal(mime_with_charset, value))
        self.assertEqual(value, mime_codec.unmarshal(mime_with_charset, data))
