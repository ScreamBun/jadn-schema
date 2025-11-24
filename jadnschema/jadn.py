"""
Basic JADN functions
"""
import os

from typing import BinaryIO, Dict, Set, TextIO, Union
from .schema import Schema


def analyze(schema: dict) -> Dict[str, Set[str]]:
    """
    Analyze the given schema for unreferenced and undefined types
    :param schema: schema to analyze
    :return: analysis results
    """
    return Schema.parse_obj(schema).analyze()


def check(schema: Union[dict, str]) -> Schema:
    """
    Validate JADN structure against JSON schema,
    Validate JADN structure against JADN schema, then
    Perform additional checks on type definitions
    :param schema: schema to check, a jADN dict or JADN str
    :return: validated schema
    """
    if isinstance(schema, dict):
        return Schema.parse_obj(schema)
    return Schema.parse_raw(schema)


def dump(schema: dict, file_name: Union[str, BinaryIO, TextIO], indent: int = 2, strip_com: bool = False, width: int = 0) -> None:
    """
    Write the JADN to a file
    :param schema: schema to write
    :param file_name: file to write to
    :param indent: spaces to indent
    :param strip_com: strip comments from schema
    :param width: max length of comment
    - length <= 0 will leave all comment unless strip is True
    """
    return Schema.parse_obj(schema).dump(file_name, indent)


def dumps(schema: dict, indent: int = 2, strip_com: bool = False, width: int = 0) -> str:
    """
    Properly format a JADN schema
    :param schema: Schema to format
    :param indent: spaces to indent
    :param strip_com: strip comments from schema
    :param width: max length of comment
        length <= 0 will leave all comment unless strip is True
    :return: Formatted JADN schema
    """
    return Schema.parse_obj(schema).dumps(indent)


def load(file_name: Union[str, BinaryIO, TextIO], extensions: Set[str] = None) -> Schema:
    """
    Load a JADN schema from a file
    :param file_name: JADN schema file to load
    :param extensions: a set of JADN extensions to simplify
        * AnonymousType:   Replace all anonymous type definitions with explicit
        * Multiplicity:    Replace all multi-value fields with explicit ArrayOf type definitions
        * DerivedEnum:     Replace all derived and pointer enumerations with explicit Enumerated type definitions
        * MapOfEnum:       Replace all MapOf types with listed keys with explicit Map type definitions
        * Link:            Replace Key and Link fields with explicit types
    :return: loaded schema
    """
    if isinstance(file_name, str):
        return Schema.parse_file(file_name).simplify(extensions)
    return Schema.parse_raw(file_name.read()).simplify(extensions)


def loads(schema: Union[bytes, dict, str], extensions: Set[str] = None) -> Schema:
    """
    load a JADN schema from a string
    :param schema: JADN schema to load
    :param extensions: JADN extensions to simplify
        * AnonymousType:   Replace all anonymous type definitions with explicit
        * Multiplicity:    Replace all multi-value fields with explicit ArrayOf type definitions
        * DerivedEnum:     Replace all derived and pointer enumerations with explicit Enumerated type definitions
        * MapOfEnum:       Replace all MapOf types with listed keys with explicit Map type definitions
        * Link:            Replace Key and Link fields with explicit types
    :return: loaded schema
    """
    if isinstance(schema, dict):
        return Schema.parse_obj(schema).simplify(extensions)
    return Schema.parse_raw(schema).simplify(extensions)


# Extra ??
def canonicalize(schema: dict) -> dict:
    """
    Sort schema into canonical order (for comparisons)
    :param schema: Schema to sort
    :return: sorted canonicalized schema
    """
    return loads(schema).schema()


def data_dir() -> str:
    """
    Return directory containing JADN schema files
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


def strip(schema: dict, width: int = 0) -> dict:
    """
    Strip/Truncate comments from schema
    :param schema: schema to strip comments
    :param width: max length of comment
        - length <= 0 will strip all comments
        - length > 0 will truncate comments to this width
    :return: comment stripped JADN schema
    """
    if width <= 0:
        return Schema.parse_obj(schema).schema(strip_comments=True, comment_width=0)
    else:
        return Schema.parse_obj(schema).schema(strip_comments=False, comment_width=width)


def unfold_extensions(schema: dict, extensions: Set[str] = None) -> Schema:
    """
    Simplify the given schema
    :param schema: schema to simplify
    :param extensions: JADN extensions
        * AnonymousType:   Replace all anonymous type definitions with explicit
        * Multiplicity:    Replace all multi-value fields with explicit ArrayOf type definitions
        * DerivedEnum:     Replace all derived and pointer enumerations with explicit Enumerated type definitions
        * MapOfEnum:       Replace all MapOf types with listed keys with explicit Map type definitions
        * Link:            Replace Key and Link fields with explicit types
    :return: simplified schema
    """
    return Schema.parse_obj(schema).simplify(extensions)
