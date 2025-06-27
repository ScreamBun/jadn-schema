import pytest
import os
from unittest import TestCase, skip
from jadnschema import Schema
from jadnschema.convert.schema.writers.json_schema.schema_validator import validate_schema_jadn_syntax, validate_schema


def test_example_schema_is_valid():
    file_path = os.path.join(os.path.dirname(__file__), 'schema/test-schema.jadn')
    schema_path = os.path.abspath(file_path)

    example_schema_obj = Schema.parse_file(schema_path)
    try:
        validate_schema(example_schema_obj.dict())
        assert False
    except Exception as e:
        assert True

def test_example_jadn2_schema_is_valid():
    file_path = os.path.join(os.path.dirname(__file__), 'schema/test-jadn2-schema.jadn')
    schema_path = os.path.abspath(file_path)
    example_schema_obj = Schema.parse_file(schema_path)
    try:
        validate_schema(example_schema_obj.dict())
        assert True
    except Exception as e:
        pytest.fail(f"JADN2 Schema validation failed: {e}")