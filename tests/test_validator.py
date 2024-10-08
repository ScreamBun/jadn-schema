import json
import os

from unittest import TestCase, skip
from pydantic import ValidationError
from jadnschema import Schema

CMD_TYPE = "OpenC2-Command"
RSP_TYPE = "OpenC2-Response"


class CommandValidation(TestCase):
    _test_root = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    # _schema = f"{_test_root}/schema/oc2ls-v1.1-lang_resolved.jadn"
    _schema = f"{_test_root}/schema/oc2ls-v1.0.1-resolved.jadn"
    with open(_schema, "r", encoding="utf-8") as f:
        _schema_json = json.load(f)    
    # _schema = f"{_test_root}/schema/test-schema.jadn"
    
    _test_schema = {
                        "info": {
                            "package": "http://test/v1.0",
                            "exports": ["Record-Test"]
                        },
                        "types": [
                            ["String-Test", "String", ["/ipv4"], ""],
                            ["Record-Test", "Record", ["{1"], "", [
                                [1, "field_value_1", "String", ["[1"], ""]
                            ]]
                        ]
                    }

    @classmethod
    def setUpClass(cls) -> None:
        cls._schema_obj = Schema.model_validate(cls._schema_json)
        cls._test_schema_obj = Schema.model_validate(cls._test_schema)
        
    def test_simple(self):
        test_err = None
        try:
            self._test_schema_obj.validate_as("Record-Test", {
                                                                "field_value_1": "213.153.57.102"
                                                             })
        except Exception as err: 
            test_err = err
            print(err)
            
        self.assertIsNone(test_err)
            

    def test_allow_mapOf(self):
        self._schema_obj.validate_as(RSP_TYPE, {
            "status": 200,
            "results": {
                "pairs": {
                    "scan": [
                        "command"
                    ]
                },
                "versions": [
                "1.1"
                ]
            }
        })

    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            self._schema_obj.validate_as(CMD_TYPE, {
                "action": "allow",
                "target": {
                    "email_addr": "test.testabc.com"
                }
            })

    def test_allow_email_Chinese_Unicode(self):
        self._schema_obj.validate_as(CMD_TYPE, {
            "action": "allow",
            "target": {
                "idn_email_addr": "用户@例子.广告"
            }
        })

    def test_allow_email_Hindi_Unicode(self):
        self._schema_obj.validate_as(CMD_TYPE, {
            "action": "allow",
            "target": {
                "idn_email_addr": "अजय@डाटा.भारत"
            }
        })

    def test_allow_email_Ukrainian_Unicode(self):
        self._schema_obj.validate_as(CMD_TYPE, {
            "action": "allow",
            "target": {
                "idn_email_addr": "квіточка@пошта.укр"
            }
        })

    def test_allow_email_Greek_Unicode(self):
        self._schema_obj.validate_as(CMD_TYPE, {
            "action": "allow",
            "target": {
                "idn_email_addr": "θσερ@εχαμπλε.ψομ"
            }
        })

    def test_allow_email_German_Unicode(self):
        self._schema_obj.validate_as(CMD_TYPE, {
            "action": "allow",
            "target": {
                "idn_email_addr": "Dörte@Sörensen.example.com"
            }
        })

    def test_allow_email_Russian_Unicode(self):
        self._schema_obj.validate_as(CMD_TYPE, {
            "action": "allow",
            "target": {
                "idn_email_addr": "коля@пример.рф"
            }
        })

    def test_allow_ipv4_conn(self):
        with self.assertRaises(ValidationError):
            self._schema_obj.validate_as(CMD_TYPE, {
                "action": "allow",
                "target": {
                    "ipv4_connection": {
                        "src_addr": "172.20.0.100",
                        "src_port": 65539
                    }
                }
            })

    def test_allow_device(self):
        self._schema_obj.validate_as(CMD_TYPE, {
            "action": "allow",
            "target": {
                "device": {
                    "hostname": "test.example.com",
                    "device_id": "device"
                }
            }
        })


class ResponseValidation(TestCase):
    _test_root = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    # _schema = f"{_test_root}/schema/oc2ls-v1.1-lang_resolved.jadn"
    _schema = f"{_test_root}/schema/oc2ls-v1.0.1-resolved.jadn"

    @classmethod
    def setUpClass(cls) -> None:
        cls._schema_obj = Schema.model_validate(cls._schema)

    def test_pairs(self):
        self._schema_obj.validate_as(RSP_TYPE, {
            "status": 200,
            "status_text": "string",
            "results": {
                "pairs": {
                    "scan": ["file"],
                    "query": ["features"]
                }
            }
        })

    def test_profiles(self):
        self._schema_obj.validate_as(RSP_TYPE, {
            "status": 200,
            "status_text": "string test",
            "results": {
                "profiles": [
                    "slpf",
                    "x-sfps"
                ]
            }
        })
