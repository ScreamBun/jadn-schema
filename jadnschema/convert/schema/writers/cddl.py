"""
JADN to CDDL
"""
import json
import re

from typing import Union
from .baseWriter import BaseWriter
from .utils import TableFormat, TableStyle
from ..enums import CommentLevels
from ....schema import Schema
from ....schema.definitions import Array, ArrayOf, Choice, Enumerated, Map, MapOf, Record, Primitive


# Conversion Class
class JADNtoCDDL(BaseWriter):
    format = "cddl"
    comment_single = ";"
    _escape_chars = []
    _fieldMap = {
        "Binary": "bstr",
        "Boolean": "bool",
        "Integer": "int64",
        "Number": "float64",
        "Null": "null",
        "String": "tstr"
    }

    def dumps(self, **kwargs) -> str:
        """
        Converts the JADN schema to CDDL
        :return: CDDL schema
        """
        doubleEmpty = re.compile("^$\n?^$", re.MULTILINE)
        return re.sub(doubleEmpty, "", f"{self.makeHeader()}{self._makeStructuresString(default='')}\n")

    def makeHeader(self):
        """
        Create the header for the schema
        :return: header for schema
        """
        header_regex = re.compile(r"(^\"|\"$)")

        def mkrow(k, v):
            if isinstance(v, dict) or hasattr(v, "schema"):
                v = v.schema() if hasattr(v, "schema") else v
                v = ", ".join([f"**{k1}**: {v1}" for k1, v1 in v.items()])
            elif isinstance(v, (list, tuple)):
                v = ", ".join([f"**{k}**: {v}" for (k, v) in v] if isinstance(v[0], list) else v) if len(v) > 0 else "N/A"
            return f"{k} - {header_regex.sub('', json.dumps(v))}"

        meta = self._schema.meta.schema()
        header = [f"{self.comment_single} meta: {mkrow(k, v)}" for k, v in meta.items()]
        return "\n".join(header) + "\n\n"

    # Structure Formats
    def _formatArray(self, itm: Array, **kwargs) -> str:  # TODO: what should this do??
        type_opts = {"type": itm.data_type}
        if opts := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = opts

        rows = []
        i = len(itm.__fields__)
        for idx, field in enumerate(itm.__fields__.values(), 1):
            info = field.field_info
            opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
            if ops := info.extra["options"].dict(exclude_unset=True):
                opts["options"] = ops
            row = [
                f"{'? ' if info.extra['options'].isOptional() else ''}{self.formatStr(field.alias)}:",
                f"{self._fieldType(field.field_info.extra['type'])}{', ' if i > idx else ''}",
                self._formatComment(info.description, jadn_opts=opts)
            ]
            rows.append(row)
            i -= 1

        properties = self._space_start.sub(self._indent, self._makeTable(
            rows=rows,
            table=TableFormat.Ascii,
            style=TableStyle.STYLE_NONE
        ))
        comment = f"\n// {itm.description}" if itm.description else ""
        jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
        jadn_comment = f"  {jadn_comment}" if jadn_comment else ""
        return f"{comment}\n{self.formatStr(itm.name)} = [{jadn_comment}\n{properties}\n]"

    def _formatArrayOf(self, itm: ArrayOf, **kwargs) -> str:  # TODO: what should this do??
        opts = itm.__options__
        field_type = f"[{opts.get('minv', '')}*{opts.get('maxv', '')} {self._fieldType(opts.get('vtype', 'string'))}]"
        type_opts = {"type": itm.data_type}
        return f"\n{self.formatStr(itm.name)} = {field_type} {self._formatComment(itm.description, jadn_opts=type_opts)}\n"

    def _formatChoice(self, itm: Choice, **kwargs) -> str:
        rows = []
        i = len(itm.__fields__)
        for idx, field in enumerate(itm.__fields__.values(), 1):
            info = field.field_info
            opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
            if ops := info.extra["options"].dict(exclude_unset=True):
                opts["options"] = ops
            rows.append([
                f"{self.formatStr(field.alias)}:",
                f"{self._fieldType(field.field_info.extra['type'])}{' // ' if i > idx else ''}",
                self._formatComment(info.description, jadn_opts=opts)
            ])

        properties = self._space_start.sub(self._indent, self._makeTable(
            rows=rows,
            table=TableFormat.Ascii,
            style=TableStyle.STYLE_NONE
        ))
        comment = f"\n// {itm.description}" if itm.description else ""
        jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
        jadn_comment = f"  {jadn_comment}" if jadn_comment else ""
        return f"{comment}\n{self.formatStr(itm.name)} = ({jadn_comment}\n{properties}\n)"

    def _formatEnumerated(self, itm: Enumerated, **kwargs) -> str:
        enum_name = self.formatStr(itm.name)
        rows = []
        i = len(itm.__enums__)
        for idx, f in enumerate(itm.__enums__, 1):
            opts = {"field": f.value.extra["id"]}
            value = self.formatStr(f.value.default or f"Unknown_{enum_name}_{f.value.extra['id']}")
            rows.append([
                f"{enum_name} {'/' if i > idx else ''}=",
                f"\"{value}\"",
                self._formatComment(f.value.description, jadn_opts=opts)
            ])

        properties = self._space_start.sub("", self._makeTable(
            rows=rows,
            table=TableFormat.Ascii,
            style=TableStyle.STYLE_NONE
        ))
        comment = f"\n{self.comment_single} {itm.description}" if itm.description else ""
        jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
        jadn_comment = f"\n{jadn_comment}" if jadn_comment else ""
        return f"{comment}{jadn_comment}\n{properties}\n"

    def _formatMap(self, itm: Map, **kwargs) -> str:
        rows = []
        i = len(itm.__fields__)
        for idx, field in enumerate(itm.__fields__.values(), 1):
            info = field.field_info
            opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
            if ops := info.extra["options"].dict(exclude_unset=True):
                opts["options"] = ops
            rows.append([
                f"{'? ' if info.extra['options'].isOptional() else ''}{self.formatStr(field.alias)}:",
                f"{self._fieldType(field.field_info.extra['type'])}{', ' if i > idx else ''}",
                self._formatComment(info.description, jadn_opts=opts)
            ])
            i -= 1

        properties = self._space_start.sub(self._indent, self._makeTable(
            rows=rows,
            table=TableFormat.Ascii,
            style=TableStyle.STYLE_NONE
        ))
        comment = f"\n// {itm.description}" if itm.description else ""
        jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
        jadn_comment = f"  {jadn_comment}" if jadn_comment else ""
        return f"{comment}\n{self.formatStr(itm.name)} = [{jadn_comment}\n{properties}\n]"

    def _formatMapOf(self, itm: MapOf, **kwargs) -> str:  # TODO: what should this do??
        # return f"FORMAT MapOf: {itm.name}"
        key = self._fieldType(itm.__options__.get('ktype', 'string'))
        val = self._fieldType(itm.__options__.get('vtype', 'string'))
        comment = f"\n// {itm.description}" if itm.description else ""
        return f"{comment}\n{self.formatStr(itm.name)} = {{* {key} => {val}}}"

    def _formatRecord(self, itm: Record, **kwargs) -> str:
        rows = []
        i = len(itm.__fields__)
        for idx, field in enumerate(itm.__fields__.values(), 1):
            info = field.field_info
            opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
            if ops := info.extra["options"].dict(exclude_unset=True):
                opts["options"] = ops
            rows.append([
                f"{'? ' if info.extra['options'].isOptional() else ''}{self.formatStr(field.alias)}:",
                f"{self._fieldType(field.field_info.extra['type'])}{',' if i > idx else ''}",
                self._formatComment(info.description, jadn_opts=opts)
            ])

        properties = self._space_start.sub(self._indent, self._makeTable(
            rows=rows,
            table=TableFormat.Ascii,
            style=TableStyle.STYLE_NONE
        ))
        comment = f"\n{self.comment_single} {itm.description}" if itm.description else ""
        jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
        jadn_comment = f"  {jadn_comment}" if jadn_comment else ""
        return f"{comment}\n{self.formatStr(itm.name)} = {{{jadn_comment}\n{properties}\n}}"

    def _formatCustom(self, itm: Union[Primitive, ArrayOf, MapOf], **kwargs) -> str:
        custom_cddl = self._formatComment(itm.description)
        custom_cddl = f"{custom_cddl}\n" if custom_cddl else ""
        return f"\n{custom_cddl}{self.comment_single} ${itm.name}({itm.data_type}) {itm.__options__.dict(exclude_unset=True)}"

    # Helper Functions
    def _fieldType(self, f: str) -> str:
        """
        Determines the field type for the schema
        :param f: current type
        :return: type mapped to the schema
        """
        if f in self._customFields:
            return self.formatStr(f)
        if f in self._fieldMap:
            return self.formatStr(self._fieldMap.get(f, f))
        return "tstr"


# Writer Functions
def cddl_dump(schema: Union[str, dict, Schema], fname: str, source: str = "", comm: CommentLevels = CommentLevels.ALL, **kwargs):
    comm = comm if comm in CommentLevels else CommentLevels.ALL
    return JADNtoCDDL(schema, comm).dump(fname, source, **kwargs)


def cddl_dumps(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs):
    comm = comm if comm in CommentLevels else CommentLevels.ALL
    return JADNtoCDDL(schema, comm).dumps(**kwargs)
