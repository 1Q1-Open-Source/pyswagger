from __future__ import absolute_import
import unittest
import uuid
import random
import base64
from os import path

from pyswagger import App
from pyswagger.primitives import Renderer, MimeCodec
from .utils import get_test_data_folder


class SmallIntegrationTestCase(unittest.TestCase):
    """Small end-to-end style tests without network I/O (Step 6).

    - Load sample Swagger 2.0 specs from tests/data.
    - Exercise renderer presets (classic vs minimal).
    - Perform JSON and HAL marshal/unmarshal cycles.
    - Validate UUID fields where present.
    """

    @classmethod
    def setUpClass(kls):
        # Specs used across tests
        kls.app_obj = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'object')
        ))
        kls.app_model = App.create(get_test_data_folder(
            version='2.0',
            which=path.join('schema', 'model')
        ))
        kls.rnd = Renderer()
        kls.codec = MimeCodec()

    def test_renderer_presets_minimal_vs_classic(self):
        random.seed(0)

        user_schema = self.app_obj.resolve('#/definitions/user')

        # Classic: may include optional fields (email)
        opt_classic = self.rnd.default('classic')
        u_classic = self.rnd.render(user_schema, opt=opt_classic)
        self.assertIn('id', u_classic)
        self.assertIn('name', u_classic)

        # Minimal: required-only by default
        opt_min = self.rnd.default('minimal')
        u_min = self.rnd.render(user_schema, opt=opt_min)
        self.assertIn('id', u_min)
        self.assertIn('name', u_min)
        # email is optional in this schema
        self.assertNotIn('email', u_min)

    def test_json_and_hal_round_trip(self):
        # Use a simple value and ensure JSON/HAL round-trip is identical
        value = {
            '_links': {'self': {'href': '/users/1'}},
            '_embedded': {'teams': [{'id': 1}, {'id': 2}]},
            'name': 'user'
        }

        # JSON
        data_json = self.codec.marshal('application/json', value)
        parsed_json = self.codec.unmarshal('application/json', data_json)
        self.assertEqual(parsed_json, value)

        # HAL should reuse JSON semantics, with and without charset param
        data_hal = self.codec.marshal('application/hal+json', value)
        parsed_hal = self.codec.unmarshal('application/hal+json', data_hal)
        self.assertEqual(parsed_hal, value)

        data_hal_charset = self.codec.marshal('application/hal+json; charset=utf-8', value)
        parsed_hal_charset = self.codec.unmarshal('application/hal+json; charset=utf-8', data_hal_charset)
        self.assertEqual(parsed_hal_charset, value)

    def test_uuid_validation_and_serialization(self):
        # Schema contains a string/uuid format definition
        uuid_schema = self.app_model.resolve('#/definitions/uuid')

        # Valid string should remain the same when str() is applied to the wrapper
        s = '550e8400-e29b-41d4-a716-446655440000'
        dv = uuid_schema._prim_(s, self.app_model.prim_factory)
        self.assertEqual(str(dv), s)

        # Construct an object with uuid.UUID and ensure outbound JSON is canonical string
        uid = uuid.uuid4()
        payload = {'id': uid}
        json_data = self.codec.marshal('application/json', payload)
        parsed = self.codec.unmarshal('application/json', json_data)
        # Value serialized as a string
        self.assertEqual(parsed['id'], str(uid))
