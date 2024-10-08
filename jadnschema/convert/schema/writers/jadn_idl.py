# """
# JADN to JADN IDL
# """
# import json

# from typing import List, Union
# from pydantic.fields import ModelField  # pylint: disable=no-name-in-module
# from .baseWriter import BaseWriter
# from .utils import Alignment, TableFormat, TableStyle
# from ..enums import CommentLevels
# from ..helpers import register_writer
# from ....schema import Schema
# from ....schema.consts import OPTION_ID
# from ....schema.definitions import Array, ArrayOf, Choice, Enumerated, Map, MapOf, Record, Primitive
# from ....utils import FrozenDict
# __pdoc__ = {
#     "JADNtoIDL.format": "File extension of the given format",
#     "JADNtoIDL.escape_chars": "Characters that are not supported in the schema format and need to be removed/escaped",
#     "JADNtoIDL.comment_multi": "Multiline comment characters; Tuple[START_CHAR, END_CHAR]",
#     "JADNtoIDL.comment_single": "Single line comment character",
# }

# FormatStyles = FrozenDict(
#     id=4,        # Width of Field ID column
# )


# """
# *******
# DEPRECATED. (9/12/24)

# Copied from JADN pypi, which has since been updated
# TODO: Eventually remove once the logic below has been verified that it is no longer needed.

# *******
# """


# # Conversion Class
# @register_writer
# class JADNtoIDL(BaseWriter):
#     format = "jidl"
#     comment_multi = ("/*", "*/")
#     comment_single = "//"

#     def dumps(self, **kwargs) -> str:
#         """
#         Converts the JADN schema to JADN IDL
#         :return: JSON schema
#         """
#         schema_jidl = self.makeHeader()
#         schema_jidl += self._makeStructuresString(default="")
#         return "\n".join(map(str.rstrip, schema_jidl.split("\n"))).replace("\t", " "*4)

#     def makeHeader(self) -> str:
#         """
#         Create the headers for the schema
#         :return: header for schema
#         """
#         info = self._schema.info.schema()
#         meta = self._makeTable(
#             rows=[[f"{k}:", json.dumps(v)] for k, v in info.items()],
#             align=[Alignment.ALIGN_RIGHT, Alignment.ALIGN_LEFT],
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         )
#         return f"{meta}\n\n"

#     # Structure Formats
#     def _formatArray(self, itm: Array, **kwargs) -> str:
#         array_idl = f"{itm.name} = Array"
#         array_idl += f" /{itm.__options__.format}" if itm.__options__.format else ""

#         itm_fields = []
#         for f in itm.__fields__.values():
#             info = f.field_info
#             opts = info.extra["options"]
#             field_type = info.extra["type"]
#             if field_type == "ArrayOf":
#                 field_type += f"({self._getType(opts.get('vtype', 'String'))})"
#             elif field_type == "MapOf":
#                 field_type += f"({self._getType(opts.get('ktype', 'String'))}, {self._getType(opts.get('vtype', 'String'))})"

#             array = f"[{opts.multiplicity()}]" if opts.isArray() else ""
#             fmt = f" /{opts.format}" if opts.format else ""
#             opt = " optional" if opts.isOptional() else ""

#             itm_fields.append([
#                 f"{info.extra['id']:>{FormatStyles.id}}",
#                 f"{field_type}{array}{fmt}{'' if array else opt}",
#                 f"{self.comment_single} {f.alias}:: {info.description}" if info.description else ""
#             ])
#         itm_fields = self._makeTable(
#             rows=itm_fields,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         )
#         return self._alignTypeDescription(array_idl, itm_fields, itm.description) + "\n"

#     def _formatArrayOf(self, itm: ArrayOf, **kwargs) -> str:
#         return self._formatCustom(itm)

#     def _formatChoice(self, itm: Choice, **kwargs) -> str:
#         choice_id = getattr(itm.__options__, "id", False)
#         choice_idl = f"{itm.name} = Choice{'.ID' if choice_id else ''}"
#         itm_fields = self._makeFields(itm.__fields__.values(), choice_id)
#         return self._alignTypeDescription(choice_idl, itm_fields, itm.description) + "\n"

#     def _formatEnumerated(self, itm: Enumerated, **kwargs) -> str:
#         enum_id = getattr(itm.__options__, "id", False)
#         enum_idl = f"{itm.name} = Enumerated{'.ID' if enum_id else ''}"

#         itm_fields = []
#         for f in itm.__enums__:
#             fid = f"{f.value.extra['id']:>{FormatStyles.id}}"
#             if enum_id:
#                 itm_fields.append([fid, f"{self.comment_single} {f.value.default}:: {f.value.description}"])
#             else:
#                 itm_fields.append([fid, f.value.default, f"{self.comment_single} {f.value.description}"])
#         itm_fields = self._makeTable(
#             rows=itm_fields,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         )
#         return self._alignTypeDescription(enum_idl, itm_fields, itm.description) + "\n"

#     def _formatMap(self, itm: Map, **kwargs) -> str:
#         map_id = getattr(itm.__options__, "id", False)
#         map_idl = f"{itm.name} = Map{'.ID' if map_id else ''}"
#         if multi := itm.__options__.multiplicity(check=lambda x, y: x > 0 or y > 0):
#             map_idl += f"{{{multi}}}"

#         itm_fields = self._makeFields(itm.__fields__.values(), map_id)
#         return self._alignTypeDescription(map_idl, itm_fields, itm.description) + "\n"

#     def _formatMapOf(self, itm: MapOf, **kwargs) -> str:
#         return self._formatCustom(itm)

#     def _formatRecord(self, itm: Record, **kwargs) -> str:
#         record_idl = f"{itm.name} = Record"
#         if multi := itm.__options__.multiplicity(check=lambda x, y: x > 0 or y > 0):
#             record_idl += f"{{{multi}}}"

#         itm_fields = self._makeFields(itm.__fields__.values())
#         return self._alignTypeDescription(record_idl, itm_fields, itm.description) + "\n"

#     def _formatCustom(self, itm: Union[Primitive, ArrayOf, MapOf], **kwargs) -> str:
#         itmType = f"{itm.data_type}"
#         opts = itm.__options__
#         if itm.data_type == "ArrayOf":
#             itmType += f"({self._getType(opts.get('vtype', 'String'))})"
#         elif itm.data_type == "MapOf":
#             itmType += f"({self._getType(opts.get('ktype', 'String'))}, {self._getType(opts.get('vtype', 'String'))})"

#         if itm.data_type in ("Integer", "Number"):
#             multi = opts.numeric_limit()
#         else:
#             multi = opts.multiplicity(check=lambda x, y: x > 0 or y > 0)
#         itmType += f"{{{multi}}}" if multi else ""

#         itmType += f" (%{opts.pattern}%)" if opts.pattern else ""
#         itmType += f" /{opts.format}" if opts.format else ""
#         itmType += " unique" if opts.get("unique", False) else ""
#         return self._alignTypeDescription(f"{itm.name} = {itmType}", "", itm.description) + "\n"

#     # Helper Functions
#     def _alignTypeDescription(self, prefix: str, fields: str, desc: str) -> str:
#         fields = fields.replace("\t", "    ")
#         if desc:
#             filler = "  "
#             if self.comment_single in fields:
#                 idx = fields.find(self.comment_single)
#                 if idx > len(prefix):
#                     filler = " " * (idx - len(prefix))
#             prefix += f"{filler}{self.comment_single} {desc}"
#         fields = f"\n{fields}" if fields else ""
#         return f"{prefix}{fields}"

#     def _makeFields(self, itm_fields: List[ModelField], opt_id: bool = False) -> str:
#         rows = []
#         for field in itm_fields:
#             info = field.field_info
#             opts = info.extra["options"]
#             field_type = info.extra["type"]
#             if field_type == "ArrayOf":
#                 field_type += f"({self._getType(opts.get('vtype', 'String'))})"
#                 field_type += f"{{{opts.multiplicity(field=False)}}}"
#             elif field_type == "MapOf":
#                 field_type += f"({self._getType(opts.get('ktype', 'String'))}, {self._getType(opts.get('vtype', 'String'))})"
#                 field_type += f"{{{opts.multiplicity(field=False)}}}"
#             elif field_type == "Enumerated":
#                 field_type += f"(Enum[{self._getType(opts.get('enum', 'String'))}])"
#             elif field_type in ("Integer", "Number"):
#                 multi = opts.numeric_limit()
#                 field_type += f"{{{multi}}}" if multi else ""

#             if opts.isArray():
#                 multi = opts.multiplicity(field=True)
#                 field_type += f" [{multi}]"
#             else:
#                 multi = opts.multiplicity(check=lambda x, y: x > 0 or y > 0)
#                 field_type += f"{{{multi}}}" if multi else ""

#             name = f"{field.alias}{'/' if opts.dir else ''}"
#             fmt = f" /{opts.format}" if opts.format else ""
#             pattern = f"(%{opts.pattern}%)" if opts.pattern else ""
#             opt = " optional" if opts.isOptional() else ""
#             unq = " unique" if opts.get("unique", False) else ""

#             if opt_id:
#                 rows.append([
#                     f"{info.extra['id']:>{FormatStyles.id}}",
#                     f"{field_type}{fmt}{pattern}{unq}{opt}",
#                     f"{self.comment_single} {name}::{info.description if info.description else ''}"
#                 ])
#             else:
#                 rows.append([
#                     f"{info.extra['id']:>{FormatStyles.id}}",
#                     name,
#                     f"{field_type}{fmt}{pattern}{unq}{opt}",
#                     f"{self.comment_single} {info.description}" if info.description else ""
#                 ])
#         return self._makeTable(
#             rows=rows,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         )

#     def _getType(self, type_: str) -> str:
#         if type_.startswith(OPTION_ID.enum):
#             return f"Enum[{type_[1:]}]"
#         if type_.startswith(OPTION_ID.pointer):
#             return f"Pointer[{type_[1:]}]"
#         return type_


# # Writer Functions
# def jidl_dump(schema: Union[str, dict, Schema], fname: str, source: str = "", comm: CommentLevels = CommentLevels.ALL, **kwargs):
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoIDL(schema, comm).dump(fname, source, **kwargs)


# def jidl_dumps(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs):
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoIDL(schema, comm).dumps(**kwargs)
