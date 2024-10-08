# """
# JADN to ProtoBuf v3
# """
# import json
# import re

# from typing import Dict, List, Union
# from urllib.parse import urlparse
# from .baseWriter import BaseWriter
# from .utils import TableFormat, TableStyle
# from ..enums import CommentLevels
# from ....schema import Schema
# from ....schema.definitions import Array, ArrayOf, Choice, Enumerated, Map, MapOf, Record, Primitive
# from ....utils import FrozenDict

# FormatStyles = FrozenDict(
#     info=12,              # Width of info name column (e.g., module:)
# )


# def uri_to_revid(uri: str) -> str:
#     u = urlparse(uri)
#     return ".".join(u.netloc.split(":")[0].split(".")[::-1] + u.path.replace(".", "-").split("/")[1:])


# # Conversion Class
# class JADNtoProto3(BaseWriter):
#     format = "proto"
#     comment_multi = ("/*", "*/")
#     comment_single = "//"
#     _fieldMap: Dict[str, str] = {
#         "Binary": "string",
#         "Boolean": "bool",
#         "Integer": "int64",
#         "Number": "string",
#         "Null": "string",
#         "String": "string"
#     }
#     _proto_imports: List[str] = []

#     def dumps(self, **kwargs) -> str:
#         """
#         Converts the JADN schema to ProtoBuf3
#         :return: Protobuf3 schema
#         """
#         imports = "".join([f"import \"{imp}\";\n" for imp in self._proto_imports])
#         return f"{self.makeHeader()}{imports}{self._makeStructuresString(default='')}\n"

#     def makeHeader(self):
#         """
#         Create the header for the schema
#         :return: header for schema
#         """
#         def mkrow(k, v) -> str:
#             if k == "package":
#                 return f"package {uri_to_revid(info[k])};"
#             return f"{self.comment_single} {k:>{FormatStyles.info}}: {json.dumps(v)}"

#         info = self._schema.info.schema()
#         header = "\n".join([
#             "syntax = \"proto3\";",
#             *[mkrow(k, v) for k, v in info.items()]
#         ])

#         return f"{header}\n\n"

#     # Structure Formats
#     def _formatArray(self, itm: Array, **kwargs) -> str:  # TODO: what should this do??
#         return self._formatCustom(itm)

#     def _formatArrayOf(self, itm: ArrayOf, **kwargs) -> str:  # TODO: what should this do??
#         return self._formatCustom(itm)

#     def _formatChoice(self, itm: Choice, **kwargs) -> str:
#         rows = []
#         for field in itm.__fields__.values():
#             info = field.field_info
#             opts = {"type": info.extra["type"]}
#             if ops := info.extra["options"].dict(exclude_unset=True):
#                 opts["options"] = ops

#             rows.append([
#                 self._fieldType(info.extra["type"]),
#                 f"{self.formatStr(field.alias)} =",
#                 f"{info.extra['id']};",
#                 self._formatComment(info.description, jadn_opts=opts)
#             ])

#         properties = self._space_start.sub(self._indent, self._makeTable(
#             rows=rows,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         ))

#         comment = f"\n{self.comment_single} {itm.description}" if itm.description else ""
#         jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
#         jadn_comment = f"  {jadn_comment}" if jadn_comment else ""
#         return self._wrapAsRecord(f"{comment}\noneof {self.formatStr(itm.name)} {{{jadn_comment}\n{properties}\n}}")

#     def _formatEnumerated(self, itm: Enumerated, **kwargs) -> str:
#         rows = []
#         default = True
#         for field in itm.__enums__:
#             f_id = field.value.extra["id"]
#             if f_id == 0:
#                 default = False
#             rows.append([
#                 f"{self.formatStr(field.value.default or f'Unknown_{self.formatStr(field.value.default)}_{f_id}')} =",
#                 f"{f_id};",
#                 self._formatComment(field.value.description)
#             ])

#         if default:
#             rows.insert(0, [
#                 f"Unknown_{itm.name.replace('-', '_')} =",
#                 "0;",
#                 f"{self.comment_single} required starting enum number for protobuf3\n"
#             ])

#         properties = self._space_start.sub(self._indent, self._makeTable(
#             rows=rows,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         ))
#         comment = f"\n{self.comment_single} {itm.description}" if itm.description else ""
#         jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
#         jadn_comment = f"  {jadn_comment}" if jadn_comment else ""
#         return f"{comment}\nenum {self.formatStr(itm.name)} {{{jadn_comment}\n{properties}\n}}"

#     def _formatMap(self, itm: Map, **kwargs) -> str:
#         return self._formatRecord(itm)

#     def _formatMapOf(self, itm: MapOf, **kwargs) -> str:  # TODO: what should this do??
#         return self._formatCustom(itm)

#     def _formatRecord(self, itm: Record, **kwargs) -> str:
#         rows = []
#         for field in itm.__fields__.values():
#             info = field.field_info
#             opts = {"type": info.extra["type"]}
#             if ops := info.extra["options"].dict(exclude_unset=True):
#                 opts["options"] = ops

#             rows.append([
#                 self._fieldType(info.extra["type"]),
#                 f"{self.formatStr(field.alias)} =",
#                 f"{info.extra['id']};",
#                 self._formatComment(info.description, jadn_opts=opts)
#             ])

#         properties = self._space_start.sub(self._indent, self._makeTable(
#             rows=rows,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         ))
#         comment = f"\n{self.comment_single} {itm.description}" if itm.description else ""
#         jadn_comment = self._formatComment(type=itm.data_type, jadn_opts=itm.__options__.dict(exclude_unset=True))
#         jadn_comment = f"  {jadn_comment}" if jadn_comment else ""
#         return f"{comment}\nmessage {self.formatStr(itm.name)} {{{jadn_comment}\n{properties}\n}}"

#     def _formatCustom(self, itm: Union[Primitive, ArrayOf, MapOf], **kwargs) -> str:
#         custom_proto = self._formatComment(itm.description)
#         custom_proto = f"{custom_proto}\n" if custom_proto else ""
#         return f"\n{custom_proto}{self.comment_single} ${itm.name}({itm.data_type}) {itm.__options__.dict(exclude_unset=True)}"

#     # Helper Functions
#     def _fieldType(self, f):
#         """
#         Determines the field type for the schema
#         :param f: current type
#         :return: type mapped to the schema
#         """
#         rtn = "string"
#         if re.search(r"(datetime|date|time)", f):
#             if "google/protobuf/timestamp.proto" not in self._proto_imports:
#                 self._proto_imports.append("google/protobuf/timestamp.proto")
#             rtn = "google.protobuf.Timestamp"

#         if f in self._customFields:
#             rtn = self.formatStr(f)

#         elif f in self._fieldMap:
#             rtn = self.formatStr(self._fieldMap.get(f, f))
#         return rtn

#     def _wrapAsRecord(self, itm: str) -> str:
#         """
#         wraps the given item as a record for the schema
#         :param itm: item to wrap
#         :return: item wrapped as a record for the schema
#         """
#         lines = list(filter(None, itm.split("\n")))
#         if len(lines) > 1:
#             n = re.search(r"\s[\w\d_]+\s", lines[0]).group()[1:-1]
#             lines = "\n".join(f"{self._indent}{l}" for l in lines)
#             return f"\nmessage {self.formatStr(n)} {{\n{lines}\n}}\n"
#         return ""


# # Writer Functions
# def proto_dump(schema: Union[str, dict, Schema], fname: str, source: str = "", comm: CommentLevels = CommentLevels.ALL, **kwargs):
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoProto3(schema, comm).dump(fname, source, **kwargs)


# def proto_dumps(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs):
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoProto3(schema, comm).dumps(**kwargs)
 