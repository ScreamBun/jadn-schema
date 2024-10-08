"""
Test JADN Messages
"""
import json
import os

from unittest import TestCase, skip
from jadnschema import Schema
from jadnschema.convert import Message, SerialFormats

schema = "oc2ls-v1.1-lang_resolved"



class Messages(TestCase):
    _test_root = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    _base_schema = f"{_test_root}/schema/{schema}.jadn"
    _base_message = f"{_test_root}/message/query_pairs.json"
    with open(_base_message, "r", encoding="utf-8") as f:
        _base_message_json = json.load(f)

    @classmethod
    def setUpClass(cls) -> None:
        cls._schema_obj = Schema.model_validate(cls._base_schema)

    def _loadMessage(self, fmt: SerialFormats):
        with open(f"{self._test_root}/message/query_pairs.{fmt}", "rb") as f:
            msg = f.read()
        msg_obj = Message.oc2_loads(msg, fmt)
        self.assertDictEqual(self._base_message_json, msg_obj.oc2_message(), f"Loaded {fmt} message is not equal to the original")

    def test_loadMessage_binn(self):
        self._loadMessage(SerialFormats.BINN)

    @skip
    def test_loadMessage_bencode(self):
        self._loadMessage(SerialFormats.BENCODE)

    def test_loadMessage_bson(self):
        self._loadMessage(SerialFormats.BSON)

    def test_loadMessage_cbor(self):
        self._loadMessage(SerialFormats.CBOR)

    def test_loadMessage_edn(self):
        self._loadMessage(SerialFormats.EDN)

    def test_loadMessage_ion(self):
        self._loadMessage(SerialFormats.ION)

    def test_loadMessage_json(self):
        self._loadMessage(SerialFormats.JSON)

    def test_loadMessage_msgpack(self):
        self._loadMessage(SerialFormats.MSGPACK)

    @skip
    def test_loadMessage_sexp(self):
        # ToDo: Verify serialization load, str/int typing
        self._loadMessage(SerialFormats.S_EXPRESSION)

    @skip
    def test_loadMessage_smile(self):
        # ToDo: Verify serialization load, `del self.error`
        self._loadMessage(SerialFormats.SMILE)

    def test_loadMessage_toml(self):
        self._loadMessage(SerialFormats.JSON)

    @skip
    def test_loadMessage_xml(self):
        # ToDo: Verify serialization load, str/float typing
        self._loadMessage(SerialFormats.XML)

    def test_loadMessage_ubjson(self):
        self._loadMessage(SerialFormats.UBJSON)

    def test_loadMessage_yaml(self):
        self._loadMessage(SerialFormats.YAML)
