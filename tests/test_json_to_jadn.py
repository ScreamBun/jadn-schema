"""
Test JADN Schema Conversions - JSON Schema to JADN
Test for json_to_jadn_dumps function
"""
import json
import os
from unittest import TestCase
from jadnschema.convert.schema.writers.js_to_jadn import json_to_jadn_dumps


def load_schema_file(filename):
    """Load a schema file from the test schema directory"""
    # Get the directory path of the current test file
    dir_path = os.path.abspath(os.path.dirname(__file__))
    schema_file_path = os.path.join(dir_path, 'schema', filename)
    
    # Read the schema file
    with open(schema_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestJSONToJADN(TestCase):
    """Test JSON Schema to JADN conversion"""

    def setUp(self):
        """Set up test data"""
        self.music_library_schema_dict = load_schema_file('music_lib.json')
        
        # Also prepare as string for testing both input formats
        self.music_library_schema_str = json.dumps(self.music_library_schema_dict)

    def test_json_to_jadn_dumps_with_string_input(self):
        """Test json_to_jadn_dumps with JSON string input"""
        result = json_to_jadn_dumps(self.music_library_schema_str)
        
        # Verify the function returns a dictionary with 'meta' and 'types' keys
        self.assertIsInstance(result, dict)
        self.assertIn('meta', result)
        self.assertIn('types', result)
        
        # Check metadata structure
        meta = result['meta']
        self.assertIsInstance(meta, dict)
        self.assertEqual(meta['package'], 'http://fake-audio.org/music-lib')
        self.assertIn('roots', meta)
        self.assertEqual(meta['roots'], ['Library'])  # Should extract from $ref
        
        # Check types structure
        types = result['types']
        self.assertIsInstance(types, list)
        self.assertGreater(len(types), 0, "Should have converted some types")

    def test_json_to_jadn_dumps_with_dict_input(self):
        """Test json_to_jadn_dumps with JSON dict input"""
        result = json_to_jadn_dumps(self.music_library_schema_dict)
        
        # Verify the function returns a dictionary with 'meta' and 'types' keys
        self.assertIsInstance(result, dict)
        self.assertIn('meta', result)
        self.assertIn('types', result)
        
        # Check metadata structure
        meta = result['meta']
        self.assertIsInstance(meta, dict)
        self.assertEqual(meta['package'], 'http://fake-audio.org/music-lib')
        
    def test_json_to_jadn_dumps_meta_contains_expected_fields(self):
        """Test that the meta section contains expected fields"""
        result = json_to_jadn_dumps(self.music_library_schema_dict)
        meta = result['meta']
        
        # Required fields
        self.assertIn('package', meta)
        self.assertIn('roots', meta)
        
        # Config is optional - only present if in source schema
        # The music library schema doesn't have a config section
        
    def test_json_to_jadn_dumps_processes_definitions(self):
        """Test that the function processes definitions from JSON Schema"""
        result = json_to_jadn_dumps(self.music_library_schema_dict)
        types = result['types']
        
        # Should have processed multiple types from definitions section
        self.assertIsInstance(types, list)
        self.assertGreater(len(types), 5, "Should have converted multiple definition types")
        
        # Each type should be a list with at least type name and type class
        for type_def in types:
            self.assertIsInstance(type_def, list)
            self.assertGreaterEqual(len(type_def), 2)
            # First element should be the type name (string)
            self.assertIsInstance(type_def[0], str)
            # Second element should be the type class (string)
            self.assertIsInstance(type_def[1], str)

    def test_json_to_jadn_dumps_with_schema_without_definitions(self):
        """Test behavior with a simple schema without definitions section"""
        simple_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/simple",
            "title": "Simple Schema",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        
        result = json_to_jadn_dumps(simple_schema)
        
        # Should still return valid structure
        self.assertIsInstance(result, dict)
        self.assertIn('meta', result)
        self.assertIn('types', result)
        
        meta = result['meta']
        self.assertEqual(meta['package'], 'http://example.org/simple')

    def test_json_to_jadn_dumps_with_defs_section(self):
        """Test schema with $defs instead of definitions"""
        schema_with_defs = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/defs-test",
            "title": "Schema with $defs",
            "$defs": {
                "Person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    }
                }
            }
        }
        
        result = json_to_jadn_dumps(schema_with_defs)
        
        # Should process $defs section
        self.assertIsInstance(result, dict)
        self.assertIn('meta', result)
        self.assertIn('types', result)
        
        types = result['types']
        self.assertGreater(len(types), 0)

    def test_json_to_jadn_dumps_handles_empty_sections_gracefully(self):
        """Test that function handles schemas with empty or missing type sections"""
        minimal_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/minimal",
            "title": "Minimal Schema"
        }
        
        # Should not raise an exception
        result = json_to_jadn_dumps(minimal_schema)
        
        self.assertIsInstance(result, dict)
        self.assertIn('meta', result)
        self.assertIn('types', result)

    def test_json_to_jadn_dumps_preserves_id_from_original_schema(self):
        """Test that the package ID is correctly extracted from $id field"""
        test_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://test.example.com/my-custom-schema",
            "title": "Test Schema",
            "definitions": {
                "TestType": {"type": "string"}
            }
        }
        
        result = json_to_jadn_dumps(test_schema)
        meta = result['meta']
        
        self.assertEqual(meta['package'], 'http://test.example.com/my-custom-schema')

    def test_json_to_jadn_dumps_extracts_root_from_ref(self):
        """Test that root type is correctly extracted from $ref field"""
        # Test with definitions reference
        schema_with_def_ref = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/test",
            "$ref": "#/definitions/MyRoot",
            "definitions": {
                "MyRoot": {"type": "object"}
            }
        }
        
        result = json_to_jadn_dumps(schema_with_def_ref)
        self.assertEqual(result['meta']['roots'], ['MyRoot'])
        
        # Test with $defs reference
        schema_with_defs_ref = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/test2",
            "$ref": "#/$defs/Person",
            "$defs": {
                "Person": {"type": "object"}
            }
        }
        
        result = json_to_jadn_dumps(schema_with_defs_ref)
        self.assertEqual(result['meta']['roots'], ['Person'])
        
        # Test without $ref (should collect all definition names as roots)
        schema_without_ref = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/test3",
            "definitions": {
                "SomeType": {"type": "object"}
            }
        }
        
        result = json_to_jadn_dumps(schema_without_ref)
        self.assertEqual(result['meta']['roots'], ['SomeType'])

    def test_json_to_jadn_dumps_handles_multiple_definitions_as_roots(self):
        """Test that multiple definitions without $ref are all included as roots"""
        schema_multiple_defs = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/multi-roots",
            "definitions": {
                "TypeA": {"type": "string"},
                "TypeB": {"type": "integer"},
                "TypeC": {"type": "object", "properties": {"name": {"type": "string"}}}
            }
        }
        
        result = json_to_jadn_dumps(schema_multiple_defs)
        roots = result['meta']['roots']
        
        # Should contain all three types as roots
        self.assertEqual(len(roots), 3)
        self.assertIn('TypeA', roots)
        self.assertIn('TypeB', roots)
        self.assertIn('TypeC', roots)

    def test_json_to_jadn_dumps_mixed_sections_as_roots(self):
        """Test that types from both definitions and $defs are included as roots"""
        schema_mixed = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/mixed",
            "definitions": {
                "DefType": {"type": "string"}
            },
            "$defs": {
                "DefsType": {"type": "integer"}
            }
        }
        
        result = json_to_jadn_dumps(schema_mixed)
        roots = result['meta']['roots']
        
        # Should contain types from both sections
        self.assertEqual(len(roots), 2)
        self.assertIn('DefType', roots)
        self.assertIn('DefsType', roots)

    def test_multiple_root_definitions_comprehensive(self):
        """Comprehensive test for multiple root level definitions logic"""
        
        # Test 1: Schema with only definitions section (multiple types)
        schema_only_definitions = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/definitions-only",
            "definitions": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"}
                    }
                },
                "Product": {
                    "type": "object", 
                    "properties": {
                        "sku": {"type": "string"},
                        "price": {"type": "number"}
                    }
                },
                "Order": {
                    "type": "object",
                    "properties": {
                        "orderId": {"type": "string"},
                        "items": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        result = json_to_jadn_dumps(schema_only_definitions)
        roots = result['meta']['roots']
        
        # Should have all three types as roots
        self.assertEqual(len(roots), 3)
        self.assertIn('User', roots)
        self.assertIn('Product', roots)
        self.assertIn('Order', roots)
        
        # Test 2: Schema with only $defs section (multiple types)
        schema_only_defs = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/defs-only",
            "$defs": {
                "Customer": {"type": "object"},
                "Invoice": {"type": "object"},
                "Payment": {"type": "object"}
            }
        }
        
        result = json_to_jadn_dumps(schema_only_defs)
        roots = result['meta']['roots']
        
        # Should have all three types as roots
        self.assertEqual(len(roots), 3)
        self.assertIn('Customer', roots)
        self.assertIn('Invoice', roots)
        self.assertIn('Payment', roots)
        
        # Test 3: Schema with both definitions and $defs (comprehensive)
        schema_both_sections = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/both-sections",
            "definitions": {
                "TypeFromDefs": {"type": "string"},
                "AnotherDefType": {"type": "integer"}
            },
            "$defs": {
                "TypeFromDollarDefs": {"type": "boolean"},
                "YetAnotherType": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
        
        result = json_to_jadn_dumps(schema_both_sections)
        roots = result['meta']['roots']
        
        # Should have all four types as roots
        self.assertEqual(len(roots), 4)
        self.assertIn('TypeFromDefs', roots)
        self.assertIn('AnotherDefType', roots)
        self.assertIn('TypeFromDollarDefs', roots)
        self.assertIn('YetAnotherType', roots)
        
        # Test 4: Schema with $ref should NOT use multiple roots logic (single root)
        schema_with_ref = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/with-ref",
            "$ref": "#/definitions/MainType",
            "definitions": {
                "MainType": {"type": "object"},
                "HelperType": {"type": "string"},
                "AnotherHelper": {"type": "integer"}
            }
        }
        
        result = json_to_jadn_dumps(schema_with_ref)
        roots = result['meta']['roots']
        
        # Should have only one root (from $ref), not all definitions
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0], 'MainType')
        
        # Test 5: Schema with no definitions/defs sections
        schema_no_defs = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/no-defs",
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        result = json_to_jadn_dumps(schema_no_defs)
        roots = result['meta']['roots']
        
        # Should have a single default root type when no definitions exist
        self.assertEqual(len(roots), 1)

    def test_config_only_included_when_present_in_source(self):
        """Test that config is only included in output when present in source schema"""
        
        # Test 1: Schema without config should not include config in output
        schema_no_config = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/no-config",
            "definitions": {
                "TestType": {"type": "string"}
            }
        }
        
        result1 = json_to_jadn_dumps(schema_no_config)
        self.assertNotIn('config', result1['meta'])
        self.assertIn('package', result1['meta'])
        self.assertIn('roots', result1['meta'])
        
        # Test 2: Schema with config should include config in output
        schema_with_config = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/with-config",
            "config": {
                "$MaxString": 500,
                "$FieldName": "^[a-zA-Z][a-zA-Z0-9_]*$",
                "customSetting": "enabled"
            },
            "definitions": {
                "TestType": {"type": "string"}
            }
        }
        
        result2 = json_to_jadn_dumps(schema_with_config)
        self.assertIn('config', result2['meta'])
        self.assertEqual(result2['meta']['config']['$MaxString'], 500)
        self.assertEqual(result2['meta']['config']['customSetting'], 'enabled')


if __name__ == '__main__':
    import unittest
    unittest.main()