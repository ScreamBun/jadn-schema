"""
Test JADN Schema Conversions - JSON Schema to JADN
Test for json_to_jadn_dumps function
"""
import json
from unittest import TestCase
from jadnschema.convert.schema.writers.js_to_jadn import json_to_jadn_dumps


class TestJSONToJADN(TestCase):
    """Test JSON Schema to JADN conversion"""

    def setUp(self):
        """Set up test data"""
        self.music_library_schema_str = '{"$schema": "http://json-schema.org/draft-07/schema#", "$id": "http://fake-audio.org/music-lib", "title": "Music Library", "version": "1.1", "description": "This information model defines a library of audio tracks, organized by album, with associated metadata regarding each track. It is modeled on the types of library data maintained by common websites and music file tag editors.", "license": "CC0-1.0", "$ref": "#/definitions/Library", "definitions": {"Library": {"title": "Library", "type": "object", "description": "Top level of the library is a map of CDs by barcode", "additionalProperties": false, "minProperties": 1, "maxProperties": 255, "properties": {"Barcode": {"$ref": "#/definitions/Barcode"}, "Album": {"$ref": "#/definitions/Album"}}}, "Barcode": {"title": "Barcode", "type": "string", "description": "A UPC-A barcode is 12 digits", "maxLength": 255, "pattern": "^\\\\d{12}$"}, "Album": {"title": "Album", "type": "object", "description": "model for the album", "additionalProperties": false, "required": ["album_artist", "album_title", "pub_data", "tracks", "total_tracks"], "maxProperties": 255, "properties": {"album_artist": {"$ref": "#/definitions/Artist", "description": "primary artist associated with this album"}, "album_title": {"type": "string", "description": "publisher\'s title for this album", "maxLength": 255}, "pub_data": {"$ref": "#/definitions/Publication-Data", "description": "metadata about the album\'s publication"}, "tracks": {"type": "array", "description": "individual track descriptions and content", "minItems": 1, "items": {"$ref": "#/definitions/Track", "description": "individual track descriptions and content"}}, "total_tracks": {"type": "integer", "description": "total track count"}, "cover_art": {"$ref": "#/definitions/Image", "description": "cover art image for this album"}}}, "Publication-Data": {"title": "Publication Data", "type": "object", "description": "who and when of publication", "additionalProperties": false, "required": ["publisher", "release_date"], "maxProperties": 255, "properties": {"publisher": {"type": "string", "description": "record label that released this album", "maxLength": 255}, "release_date": {"type": "string", "description": "and when did they let this drop", "format": "date", "maxLength": 255}}}, "Image": {"title": "Image", "type": "object", "description": "pretty picture for the album or track", "additionalProperties": false, "required": ["image_format", "image_content"], "maxProperties": 255, "properties": {"image_format": {"$ref": "#/definitions/Image-Format", "description": "what type of image file?"}, "image_content": {"type": "string", "description": "the image data in the identified format", "contentEncoding": "base64url"}}}, "Image-Format": {"title": "Image Format", "type": "string", "description": "can only be one, but can extend list", "enum": ["PNG", "JPG", "GIF"]}, "Artist": {"title": "Artist", "type": "object", "description": "interesting information about a performer", "additionalProperties": false, "required": ["artist_name", "instruments"], "maxProperties": 255, "properties": {"artist_name": {"type": "string", "description": "who is this person", "maxLength": 255}, "instruments": {"type": "array", "description": "and what do they play", "uniqueItems": true, "minItems": 1, "items": {"$ref": "#/definitions/Instrument", "description": "and what do they play"}}}}, "Instrument": {"title": "Instrument", "type": "string", "description": "collection of instruments (non-exhaustive)", "enum": ["vocals", "guitar", "bass", "drums", "keyboards", "percussion", "brass", "woodwinds", "harmonica"]}, "Track": {"title": "Track", "type": "object", "description": "for each track there\'s a file with the audio and a metadata record", "additionalProperties": false, "required": ["location", "metadata"], "maxProperties": 255, "properties": {"location": {"$ref": "#/definitions/File-Path", "description": "path to the audio file location in local storage"}, "metadata": {"$ref": "#/definitions/Track-Info", "description": "description of the track"}}}, "Track-Info": {"title": "Track Info", "type": "object", "description": "information about the individual audio tracks", "additionalProperties": false, "required": ["track_number", "title", "length", "audio_format", "genre"], "maxProperties": 255, "properties": {"track_number": {"type": "integer", "description": "track sequence number"}, "title": {"type": "string", "description": "track title", "maxLength": 255}, "length": {"type": "integer", "description": "length of track in seconds; anticipated user display is mm:ss; minimum length is 1 second"}, "audio_format": {"$ref": "#/definitions/Audio-Format", "description": "format of the digital audio"}, "featured_artist": {"type": "array", "description": "notable guest performers", "uniqueItems": true, "minItems": 1, "items": {"$ref": "#/definitions/Artist", "description": "notable guest performers"}}, "track_art": {"$ref": "#/definitions/Image", "description": "each track can have optionally have individual artwork"}, "genre": {"$ref": "#/definitions/Genre", "description": ""}}}, "Audio-Format": {"title": "Audio Format", "type": "string", "description": "can only be one, but can extend list", "enum": ["MP3", "OGG", "FLAC", "MP4", "AAC", "WMA", "WAV"]}, "Genre": {"title": "Genre", "type": "string", "description": "Enumeration of common genres", "enum": ["rock", "jazz", "hip_hop", "electronic", "folk_country_world", "classical", "spoken_word"]}, "File-Path": {"title": "File Path", "type": "string", "description": "local storage location of file with directory path from root, filename, and extension", "maxLength": 255}}}'
        
        # Also prepare as dict for testing both input formats
        self.music_library_schema_dict = json.loads(self.music_library_schema_str)

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
        self.assertEqual(meta['roots'], ['$Root'])
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


if __name__ == '__main__':
    import unittest
    unittest.main()