"""
Test JADN Schema transformations
Transformation -> Reduce Complexity
"""
import os

from typing import Callable
from unittest import TestCase, skip
from jadnschema import Schema, convert

# Consts
schema = 'oc2ls-v1.1-lang_resolved'


class Conversions(TestCase):
    _test_root = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    _base_schema = f'{_test_root}/schema/{schema}.jadn'
    _test_dir = f'{_test_root}/schema_gen'

    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.isdir(cls._test_dir):
            os.makedirs(cls._test_dir)
        cls._schema_obj = Schema.parse_file(cls._base_schema)

    def _multi_comment_dump(self, fun: Callable, fname: str, **kwargs):
        for comm in convert.CommentLevels:
            fun(self._schema_obj, f"{fname}.{comm}", comm=comm, **kwargs)

    def test_CDDL(self):
        self._multi_comment_dump(convert.cddl_dump, os.path.join(self._test_dir, schema))
        # convert.cddl_load(open(os.path.join(self._test_dir, schema + '.all.cddl'), 'rb').read(), os.path.join(self._test_dir, schema + '.cddl.jadn'))

    def test_GraphViz(self):
        self._multi_comment_dump(convert.dot_dump, os.path.join(self._test_dir, schema))

    def test_HTML(self):
        convert.html_dump(self._schema_obj, os.path.join(self._test_dir, schema))

    def test_JADN(self):
        self._multi_comment_dump(convert.jadn_dump, os.path.join(self._test_dir, schema))

    @skip
    def test_JAS(self):
        self._multi_comment_dump(convert.jas_dump, os.path.join(self._test_dir, schema))
        # convert.jas_load(open(os.path.join(self._test_dir, schema + '.jas'), 'rb').read(), os.path.join(self._test_dir, schema + '.jas.jadn'))

    def test_JIDL(self):
        self._multi_comment_dump(convert.jidl_dump, os.path.join(self._test_dir, schema))
        # with open(os.path.join(self._test_dir, schema + '.jidl.jadn'), "w") as f:
        #     convert.jidl_loads(open(os.path.join(self._test_dir, schema + '.jidl'), 'rb').read()).dump(f)

    def test_JSON(self):
        for e in convert.JsonEnumStyle:
            for i in convert.JsonImportStyle:
                self._multi_comment_dump(convert.json_dump, os.path.join(self._test_dir, schema), enum=e, imp=i)
                # convert.json_dump(self._schema_obj, os.path.join(self._test_dir, schema + '.none.{e}.{i}'), comm=convert.CommentLevels.NONE, enum=e, imp=i)
        # convert.json_load(open(os.path.join(self._test_dir, schema + '.all.json'), 'rb').read(), os.path.join(self._test_dir, schema + '.json.jadn'))

    def test_MarkDown(self):
        self._multi_comment_dump(convert.md_dump, os.path.join(self._test_dir, schema))

    def test_ProtoBuf(self):
        self._multi_comment_dump(convert.proto_dump, os.path.join(self._test_dir, schema))
        # convert.proto_load(open(os.path.join(self._test_dir, schema + '.all.proto'), 'rb').read(), os.path.join(self._test_dir, schema + '.proto.jadn'))

    def test_Relax_NG(self):
        self._multi_comment_dump(convert.relax_dump, os.path.join(self._test_dir, schema))
        # convert.relax_load(open(os.path.join(self._test_dir, schema + '.all.rng'), 'rb').read(), os.path.join(self._test_dir, schema + '.rng.jadn'))

    def test_Thrift(self):
        self._multi_comment_dump(convert.thrift_dump, os.path.join(self._test_dir, schema))
        # convert.thrift_load(open(os.path.join(self._test_dir, schema + '.all.thrift'), 'rb').read(), os.path.join(self._test_dir, schema + '.thrift.jadn'))

    @skip
    def test_XSD(self):
        self._multi_comment_dump(convert.xsd_dump, os.path.join(self._test_dir, schema))
        # convert.relax_load(open(os.path.join(self._test_dir, schema + '.all.rng'), 'rb').read(), os.path.join(self._test_dir, schema + '.rng.jadn'))

    # Tester Functions
    def test_Analyze(self):
        analysis = self._schema_obj.analyze()
        self.assertFalse(analysis["unreferenced"], f"Unreferenced Types: {', '.join(analysis['unreferenced'])}")
        self.assertFalse(analysis["undefined"], f"Undefined Types: {', '.join(analysis['undefined'])}")

    def test_Unfold(self):
        with open(os.path.join(self._test_dir, schema + '.init_simple.jadn'), "w") as f:
            self._schema_obj.dump(f)

        simple_schema = self._schema_obj.simplify()
        with open(os.path.join(self._test_dir, schema + '.simple.jadn'), "w") as f:
            simple_schema.dump(f)

    def test_prettyFormat(self):
        self._schema_obj.dump(f"{self._test_dir}/{schema}_reorg.jadn")
