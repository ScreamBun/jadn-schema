# """
# JADN to Thrift
# """
# import json
# import re

# from typing import Union
# from .baseWriter import BaseWriter
# from .utils import TableFormat, TableStyle
# from ..enums import CommentLevels
# from ....schema import Schema
# from ....schema.definitions import Array, ArrayOf, Choice, Enumerated, Map, MapOf, Record, Primitive

# FieldMap = {
#     'Binary': 'binary',
#     'Boolean': 'bool',
#     'Integer': 'i64',
#     'Number': 'double',
#     'Null': 'null',
#     'String': 'string'
# }


# # Conversion Class
# class JADNtoThrift(BaseWriter):
#     format = "thrift"
#     comment_multi = ("//", "")
#     comment_single = "//"
#     _imports = []

#     def dumps(self, **kwargs) -> str:
#         """
#         Converts the JADN schema to Thrift
#         :return: Thrift schema
#         """
#         imports = ''.join([f'import \"{imp}\";\n' for imp in self._imports])
#         return f'{self.makeHeader()}{imports}{self._makeStructuresString()}\n'

#     def makeHeader(self):
#         """
#         Create the header for the schema
#         :return: header for schema
#         """
#         header_regex = re.compile(r'(^\"|\"$)')
#         info = self._schema.info.schema()
#         header = [
#             '/*',
#             *[f" * meta: {k} - {header_regex.sub('', json.dumps(v))}" for k, v in info.items()],
#             '*/'
#         ]
#         return '\n'.join(header) + '\n\n'

#     # Structure Formats
#     def _formatArray(self, itm: Array, **kwargs) -> str:
#         # TODO: should this be another option in thrift??
#         # Best method for creating some type of array
#         # return self._formatArrayOf(itm)
#         return f"FORMAT ArrayOf: {itm.name}\n"

#     def _formatArrayOf(self, itm: ArrayOf, **kwargs) -> str:
#         # TODO: should this be another option in thrift??
#         # Best method for creating some type of array
#         nested_type = self.formatStr(itm.__options__.get('vtype', 'string'))
#         comment = self._formatComment(itm.description, type=itm.data_type, options=itm.__options__.dict(exclude_unset=True))
#         nested_def = f'{self._indent}1: optional list<{nested_type}> item; {comment}\n'
#         return f'struct {self.formatStr(itm.name)} {{\n{nested_def}}}\n'

#     def _formatChoice(self, itm: Choice, **kwargs) -> str:
#         # Thrift does not use choice, using struct
#         rows = []
#         for field in itm.__fields__.values():
#             info = field.field_info
#             rows.append([
#                 f"{info.extra['id']}:",
#                 "optional",
#                 self._fieldType(info.extra['type']),
#                 f"{self.formatStr(field.alias)};",
#                 self._formatComment(info.description, type=info.extra['type'], options=info.extra['options'].dict(exclude_unset=True))
#             ])

#         properties = self._space_start.sub(self._indent, self._makeTable(
#             rows=rows,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         ))
#         comment = self._formatComment(itm.description, type=itm.data_type, options=itm.__options__.dict(exclude_unset=True))
#         properties = self._space_start.sub(self._indent, str(properties))
#         return f'struct {self.formatStr(itm.name)} {{ {comment}\n{properties}\n}}\n'

#     def _formatEnumerated(self, itm: Enumerated, **kwargs) -> str:
#         rows = []
#         for field in itm.__enums__:
#             f_id = field.value.extra["id"]
#             rows.append([
#                 f"{self.formatStr(field.value.default or f'Unknown_{self.formatStr(field.value.default)}_{f_id}')} =",
#                 f"{f_id};",
#                 self._formatComment(field.value.description)
#             ])

#         properties = self._space_start.sub(self._indent, self._makeTable(
#             rows=rows,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         ))
#         comment = self._formatComment(itm.description, type=itm.data_type, options=itm.__options__.dict(exclude_unset=True))
#         properties = self._space_start.sub(self._indent, str(properties))
#         return f'enum {self.formatStr(itm.name)} {{ {comment}\n{properties}\n}}\n'

#     def _formatMap(self, itm: Map, **kwargs) -> str:
#         # Thrift does not use maps in same way, using struct
#         return self._formatChoice(itm)

#     def _formatMapOf(self, itm: MapOf, **kwargs) -> str:
#         # Thrift does not use maps in same way, using struct
#         # return self._formatChoice(itm)
#         return f"FORMAT MapOf: {itm.name}\n"

#     def _formatRecord(self, itm: Record, **kwargs) -> str:
#         rows = []
#         for field in itm.__fields__.values():
#             info = field.field_info
#             rows.append([
#                 f"{info.extra['id']}:",
#                 'optional' if info.extra['options'].isOptional() else 'required',
#                 self._fieldType(info.extra["type"]),
#                 f"{self.formatStr(field.alias)};",
#                 self._formatComment(info.description, type=info.extra["type"], options=info.extra["options"].dict(exclude_unset=True))
#             ])

#         properties = self._space_start.sub(self._indent, self._makeTable(
#             rows=rows,
#             table=TableFormat.Ascii,
#             style=TableStyle.STYLE_NONE
#         ))
#         comment = self._formatComment(itm.description, type=itm.data_type, options=itm.__options__.dict(exclude_unset=True))
#         properties = self._space_start.sub(self._indent, str(properties))
#         return f'struct {self.formatStr(itm.name)} {{ {comment}\n{properties}\n}}\n'

#     def _formatCustom(self, itm: Union[Primitive, ArrayOf, MapOf], **kwargs) -> str:
#         comment = self._formatComment(itm.description, type=itm.data_type, options=itm.__options__.dict(exclude_unset=True))
#         return f"{self.comment_single} {itm.name} {comment}"

#     # Helper Functions
#     def _fieldType(self, f):
#         """
#         Determines the field type for the schema
#         :param f: current type
#         :return: type mapped to the schema
#         """
#         if f in self._customFields:
#             rtn = self.formatStr(f)
#         elif f in FieldMap:
#             rtn = self.formatStr(FieldMap.get(f, f))
#         else:
#             rtn = 'string'
#         return rtn


# # Writer Functions
# def thrift_dump(schema: Union[str, dict, Schema], fname: str, source: str = "", comm: CommentLevels = CommentLevels.ALL, **kwargs):
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoThrift(schema, comm).dump(fname, source, **kwargs)


# def thrift_dumps(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs):
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoThrift(schema, comm).dumps(**kwargs)
