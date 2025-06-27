"""
Base JADN Schema Writer
"""
import json
import re

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Tuple, Union
from terminaltables import GithubFlavoredMarkdownTable
from .utils import Alignment, ColumnAlignment, TableFormat, TableStyle
from ..enums import CommentLevels
from ....exceptions import FormatError
from ....schema import Schema
from ....schema.definitions import (
    Definition, Array, ArrayOf, Choice, Enumerated, Map, MapOf, Record, Binary, Boolean, Integer, Number, String
)
from ....utils import FrozenDict
__pdoc__ = {
    "BaseWriter.format": "File extension of the given format",
    "BaseWriter.escape_chars": "Characters that are not supported in the schema format and need to be removed/escaped",
    "BaseWriter.comment_multi": "Multiline comment characters; Tuple[START_CHAR, END_CHAR]",
    "BaseWriter.comment_single": "Single line comment character"
}


class BaseWriter:
    format: str = None
    escape_chars: Tuple[str, ...] = (" ", )
    replace_chars: Dict[str, str] = {}
    comment_multi: Tuple[str, str] = ("<!--", "-->")
    comment_single: str = ""
    # Helper Vars
    _schema: Schema
    _roots: List[str]
    _comm: CommentLevels
    _customFields = Dict[str, str]
    # Non Override
    _definition_order: Tuple[str, ...] = ()
    _indent: str = " " * 2
    _space_start = re.compile(r"^\s+", re.MULTILINE)
    _title_overrides: Dict[str, str] = {}
    _table_field_headers: FrozenDict = FrozenDict({
        "ID": "id",
        "Name": ("name", "value"),
        "Value": "value",
        "Type": "type",
        "Definition": "definition",
        "#": "options",
        "Description": "description"
    })

    def __init__(self, schema: Union[dict, str, Schema], comm: str = CommentLevels.ALL):
        if isinstance(schema, Schema):
            self._schema = schema
        elif isinstance(schema, dict):
            self._schema = Schema.parse_obj(schema)
        elif Path(schema).exists():
            self._schema = Schema.parse_file(schema)
        else:
            self._schema = Schema.parse_raw(schema)
        self._roots = getattr(self._schema.meta, "roots", [])
        self._comm = comm if comm in CommentLevels else CommentLevels.ALL
        self._customFields = {t.name: t.data_type for t in self._schema.types.values()}

    def dump(self, fname: Union[str, Path], source: str = None, **kwargs) -> NoReturn:
        """
        Convert the JADN schema to another format and write it to the given file
        :param fname: schema file to write
        :param source: source information
        :param kwargs: key/value args to use for conversion
        :return:
        """
        output = fname if fname.endswith(self.format) else f"{fname}.{self.format}"
        with open(output, "w", encoding="UTF-8") as f:
            if source:
                prefix, suffix = self.comment_multi
                f.write(f"{prefix} Generated from {source}, {datetime.ctime(datetime.now())} {suffix}\n".strip())
            f.write(self.dumps(**kwargs))

    def dumps(self, **kwargs) -> Any:
        """
        Convert the JADN schema to another format
        :param kwargs: key/value args to use for conversion
        :return: converted schema
        """
        raise NotImplementedError

    # Structure Formats
    def _formatCustom(self, itm: Definition, **kwargs) -> Union[dict, str, None]:
        raise FormatError(f"{self.__class__.__name__}: format {itm.name}({itm.data_type}) not converted")

    # Structures
    def _formatArray(self, itm: Array, **kwargs) -> Union[dict, str, None]:
        raise NotImplementedError

    def _formatArrayOf(self, itm: ArrayOf, **kwargs) -> Union[dict, str, None]:
        raise NotImplementedError

    def _formatChoice(self, itm: Choice, **kwargs) -> Union[dict, str, None]:
        raise NotImplementedError

    def _formatEnumerated(self, itm: Enumerated, **kwargs) -> Union[dict, str, None]:
        raise NotImplementedError

    def _formatMap(self, itm: Map, **kwargs) -> Union[dict, str, None]:
        raise NotImplementedError

    def _formatMapOf(self, itm: MapOf, **kwargs) -> Union[dict, str, None]:
        raise NotImplementedError

    def _formatRecord(self, itm: Record, **kwargs) -> Union[dict, str, None]:
        raise NotImplementedError

    # Primitives
    def _formatBinary(self, itm: Binary, **kwargs) -> Union[dict, str, None]:
        return self._formatCustom(itm, **kwargs)

    def _formatBoolean(self, itm: Boolean, **kwargs) -> Union[dict, str, None]:
        return self._formatCustom(itm, **kwargs)

    def _formatInteger(self, itm: Integer, **kwargs) -> Union[dict, str, None]:
        return self._formatCustom(itm, **kwargs)

    def _formatNumber(self, itm: Number, **kwargs) -> Union[dict, str, None]:
        return self._formatCustom(itm, **kwargs)

    def _formatString(self, itm: String, **kwargs) -> Union[dict, str, None]:
        return self._formatCustom(itm, **kwargs)

    # Helpers
    def _formatComment(self, msg="", **kwargs):
        """
        Format a comment for the given schema
        :param msg: comment text
        :param kwargs: key/value comments
        :return: formatted comment
        """
        if self._comm == CommentLevels.NONE:
            return ""

        com = self.comment_single
        if msg not in ["", None, " "]:
            com += f" {msg}"

        if def_type := kwargs.pop("type", None):
            com += f" ${def_type}"
            com += f" {kwargs.pop('jadn_opts')}" if "jadn_opts" in kwargs else ""

        for k, v in kwargs.items():
            com += f" #{k}:{json.dumps(v)}"
        return "" if re.match(r"^;\s+$", com) else com

    def _makeStructures(self, default: Any = None, **kwargs) -> Dict[str, Union[dict, str]]:
        structs = {}
        for def_name in self._definition_order:
            if def_cls := self._schema.types.get(def_name):
                df = getattr(self, f"_format{def_cls.data_type}", self._formatCustom)
                if conv := df(itm=def_cls, **kwargs):
                    structs[def_name] = conv
                else:
                    structs[def_name] = default

        for def_name, def_cls in self._schema.types.items():
            if def_name not in self._definition_order:
                df = getattr(self, f"_format{def_cls.data_type}", self._formatCustom)
                if conv := df(itm=def_cls, **kwargs):
                    structs[def_name] = conv
                else:
                    structs[def_name] = default
        return structs

    def _makeStructuresString(self, default: Any = None, **kwargs) -> str:
        defs = self._makeStructures(default, **kwargs)
        def_strs = []
        for def_name in self._definition_order:
            def_strs.append(defs.pop(def_name, ""))
        def_strs.extend(defs.values())
        return "\n".join(def_strs)

    def _makeTable(self, rows: List[List[Union[str, int]]], align: ColumnAlignment = None, headers: List[str] = None, table: TableFormat = TableFormat.Ascii, style: TableStyle = None) -> str:
        inst = table.value(
            table_data=rows
        )
        if not isinstance(inst, GithubFlavoredMarkdownTable) and style:
            for k, v in style.value.items():
                setattr(inst, k, v)
        if headers:
            inst.table_data.insert(0, headers)
        else:
            inst.inner_heading_row_border = False

        alignment = {k: Alignment.ALIGN_LEFT for k in range(10)}
        if align:
            align = dict(enumerate(align)) if isinstance(align, list) else align
            alignment.update({k: v for k, v in align.items() if v})
        inst.justify_columns = alignment
        return inst.table

    def escapeStr(self, s: str) -> str:
        """
        escape a string for the given schema format
        :param s: string to format
        :return: formatted string
        """
        rtn = s
        for orig, repl in self.replace_chars.items():
            if orig in rtn:
                rtn = re.sub(orig, repl, rtn)
        return rtn

    def formatStr(self, s: str) -> str:
        """
        Format a string for the given schema format
        :param s: string to format
        :return: formatted string
        """
        if s == "*":
            return "unknown"
        escape_chars = list(filter(None, self.escape_chars))
        if len(escape_chars) > 0:
            return re.compile(rf"[{''.join(escape_chars)}]").sub("_", s)
        return s

    def formatTitle(self, title: str) -> str:
        """
        Format a title string for the given schema format
        :param title: string to format
        :return: formatted string
        """
        words = [self._title_overrides.get(w, w) for w in title.split("-")]
        return " ".join(words)
