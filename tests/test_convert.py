"""
Test JADN Schema Conversions
Conversions -> JADN to ...
"""
import os

from unittest import TestCase
from jadnschema import convert, jadn


# TODO: Read and Write JIDL and HTML, Write Markdown, JSON Schema, XSD, CDDL
dir_path = os.path.abspath(os.path.dirname(__file__))
quickstart_schema = {
    'structures': [
        ['Person', 'Record', [], 'JADN equivalent of structure from https://developers.google.com/protocol-buffers', [
            [1, 'name', 'String', [], ''],
            [2, 'id', 'Integer', [], ''],
            [3, 'email', 'String', ['/email', '[0'], '']
        ]]
    ]
}


class BasicConvert(TestCase): 
    def _convert(self, schema):
        raise NotImplemented(f'The unittest class `{self.__class__.__name__}` should implement _convert')

    def test_0_quickstart(self):
        self._convert(jadn.check(quickstart_schema))

    def test_1_types(self):
        schema = os.path.join(dir_path, 'schema/convert_types.jadn')
        jadn.check(schema)
        self._convert(jadn.load(schema))

    def test_2_jadn(self):
        schema = os.path.join(jadn.data_dir(), 'jadn_v1.0_schema.jadn')
        jadn.check(schema)
        self._convert(jadn.load(schema))

    def test_3_examples(self):
        schema = os.path.join(dir_path, 'schema/jadn-v1.0-examples.jadn')
        jadn.check(schema)
        self._convert(jadn.load(schema))


class HtmlConvert(BasicConvert, TestCase):
    def _convert(self, schema):
        html_doc = convert.html_dumps(schema)
        # schema_new = convert.html_loads(html_doc)
        # self.assertEqual(jadn.canonicalize(schema), jadn.canonicalize(schema_new))


class JidlConvert(BasicConvert, TestCase):
    def _convert(self, schema):
        jidl_doc = convert.jidl_dumps(schema)
        # schema_new = convert.jidl_loads(jidl_doc)
        # self.maxDiff = None
        # self.assertEqual(jadn.canonicalize(schema), jadn.canonicalize(schema_new))


# TODO: Read formats, compare to expected valid schema
class CddlConvert(BasicConvert, TestCase):
    def _convert(self, schema):
        cddl_doc = convert.cddl_dumps(schema)
        # schema_new = convert.cddl_loads(cddl_doc, fmt)
        # self.maxDiff = None
        # self.assertEqual(jadn.canonicalize(schema), jadn.canonicalize(schema_new))


class JsonConvert(BasicConvert, TestCase):
    def _convert(self, schema):
        json_doc = convert.json_dumps(schema)
        # schema_new = convert.json_loads(cddl_doc, fmt)
        # self.maxDiff = None
        # self.assertEqual(jadn.canonicalize(schema), jadn.canonicalize(schema_new))


class MarkdownConvert(BasicConvert, TestCase):
    def _convert(self, schema):
        markdown_doc = convert.md_dumps(schema)
        # schema_new = convert.md_loads(markdown_doc, fmt)
        # self.maxDiff = None
        # self.assertEqual(jadn.canonicalize(schema), jadn.canonicalize(schema_new))


'''
class XsdConvert(BasicConvert, TestCase):
    def _convert(self, schema):
        xsd_doc = convert.xsd_dumps(schema, fmt)
        # schema_new = convert.xsd_loads(markdown_doc, fmt)
        # self.maxDiff = None
        # self.assertEqual(jadn.canonicalize(schema), jadn.canonicalize(schema_new))
'''
