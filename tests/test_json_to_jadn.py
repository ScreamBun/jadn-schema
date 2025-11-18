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
        self.assertIn('config', meta)
        
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
        self.assertIn('config', meta)
        
        # Check config contains expected JADN configuration
        config = meta['config']
        self.assertIn('$MaxString', config)
        self.assertIn('$FieldName', config)
        self.assertEqual(config['$MaxString'], 1000)
        
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
        
        # Test without $ref (should default to $Root)
        schema_without_ref = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://example.org/test3",
            "definitions": {
                "SomeType": {"type": "object"}
            }
        }
        
        result = json_to_jadn_dumps(schema_without_ref)
        self.assertEqual(result['meta']['roots'], ['$Root'])


if __name__ == '__main__':
    import unittest
    unittest.main()