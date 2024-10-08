# """
# JADN to Markdown tables
# """
# from typing import Dict, List, Union
# from pydantic.fields import ModelField  # pylint: disable=no-name-in-module
# from .baseWriter import BaseWriter
# from .utils import Alignment, TableFormat
# from ..enums import CommentLevels
# from ..helpers import register_writer
# from ....schema import Schema
# from ....schema.definitions import Options, Array, ArrayOf, Choice, Enumerated, Map, MapOf, Record, Primitive
# __pdoc__ = {
#     "JADNtoMD.format": "File extension of the given format",
#     "JADNtoMD.escape_chars": "Characters that are not supported in the schema format and need to be removed/escaped",
#     "JADNtoMD.comment_multi": "Multiline comment characters; Tuple[START_CHAR, END_CHAR]",
#     "JADNtoMD.comment_single": "Single line comment character",
# }


# """
# *******
# DEPRECATED. (9/12/24)

# Copied from JADN pypi, which has since been updated
# TODO: Eventually remove once the logic below has been verified that it is no longer needed.

# *******
# """


# # Conversion Class
# @register_writer
# class JADNtoMD(BaseWriter):
#     format = "md"

#     def dumps(self, **kwargs) -> str:
#         schema_md = self.makeHeader()
#         schema_md += self._makeStructuresString(default="")
#         return schema_md.replace("\t", " "*4)

#     def makeHeader(self) -> str:
#         """
#         Create the headers for the schema
#         :return: header for schema
#         """
#         def mkrow(k, v):
#             if isinstance(v, dict) or hasattr(v, "schema"):
#                 v = v.schema() if hasattr(v, "schema") else v
#                 v = " ".join([f"**{k1}**: {v1}" for k1, v1 in v.items()])
#             elif isinstance(v, (list, tuple)):
#                 v = ", ".join(v)
#             return [f"**{k}:**", v]

#         info = self._schema.info.schema()
#         meta_table = self._makeTable(
#             rows=[mkrow(k, info[k]) for k, v in info.items()],
#             align=[Alignment.ALIGN_RIGHT],
#             headers=[".", "."],
#             table=TableFormat.MarkDown
#         )
#         return f"## Schema\n{meta_table}\n\n"

#     # Structure Formats
#     def _formatArray(self, itm: Array, **kwargs) -> str:
#         fmt = f" /{itm.__options__.format}" if itm.__options__.format else ""
#         array_md = f"**_Type: {itm.name} (Array{fmt})_**\n\n"
#         headers = ["ID", "Type", "#", "Description"]
#         rows = []
#         for f in itm.__fields__.values():
#             info = f.field_info
#             rows.append([info.extra["id"], info.extra["type"], info.extra["options"].multiplicity(1, 1, True), f"{info.alias}:: {info.description}"])
#         array_md += self._makeTable(
#             rows=rows,
#             align=[Alignment.ALIGN_RIGHT, None, Alignment.ALIGN_RIGHT],
#             headers=headers,
#             table=TableFormat.MarkDown
#         )
#         return f"{array_md}\n"

#     def _formatArrayOf(self, itm: ArrayOf, **kwargs) -> str:
#         return self._formatCustom(itm)

#     def _formatChoice(self, itm: Choice, **kwargs) -> str:
#         fmt = ".ID" if getattr(itm.__options__, "id", False) else ""
#         choice_md = f"**_Type: {itm.name} (Choice{fmt})_**\n\n"
#         headers = ["ID", "Name", "Type", "#", "Description"]
#         rows = [self._makeField(f, headers) for f in itm.__fields__.values()]
#         choice_md += self._makeTable(
#             rows=rows,
#             align=[Alignment.ALIGN_RIGHT, None, None, Alignment.ALIGN_RIGHT],
#             headers=headers,
#             table=TableFormat.MarkDown
#         )
#         return f"{choice_md}\n"

#     def _formatEnumerated(self, itm: Enumerated, **kwargs) -> str:
#         fmt = ".ID" if getattr(itm.__options__, "id", False) else ""
#         enumerated_md = f"**_Type: {itm.name} (Enumerated{fmt})_**\n\n"

#         alignment = [Alignment.ALIGN_RIGHT]
#         rows = []
#         if getattr(itm.__options__, "id", False):
#             headers = ["ID", "Description"]
#             for f in itm.__enums__:
#                 rows.append([f.value.extra["id"], f"**{f.value.default}**::{f.value.description}"])
#         else:
#             headers = ["ID", "Name", "Description"]
#             for f in itm.__enums__:
#                 rows.append([f.value.extra["id"], f"**{f.value.default}**", f.value.description])

#         enumerated_md += self._makeTable(
#             rows=rows,
#             align=alignment,
#             headers=headers,
#             table=TableFormat.MarkDown
#         )
#         return f"{enumerated_md}\n"

#     def _formatMap(self, itm: Map, **kwargs) -> str:
#         fmt = ".ID" if getattr(itm.__options__, "id", False) else ""
#         multi = itm.__options__.multiplicity(check=lambda x, y: x > 0 or y > 0)
#         fmt += f"{{{multi}}}" if multi else ""

#         map_md = f"**_Type: {itm.name} (Map{fmt})_**\n\n"
#         headers = ["ID", "Name", "Type", "#", "Description"]
#         rows = [self._makeField(f, headers) for f in itm.__fields__.values()]
#         map_md += self._makeTable(
#             rows=rows,
#             align=[Alignment.ALIGN_RIGHT, None, None, Alignment.ALIGN_RIGHT],
#             headers=headers,
#             table=TableFormat.MarkDown
#         )
#         return f"{map_md}\n"

#     def _formatMapOf(self, itm: MapOf, **kwargs) -> str:
#         return self._formatCustom(itm)

#     def _formatRecord(self, itm: Record, **kwargs) -> str:
#         fmt = f" /{itm.__options__.format}" if itm.__options__.format else ""
#         multi = itm.__options__.multiplicity(check=lambda x, y: x > 0 or y > 0)
#         fmt += f"{{{multi}}}" if multi else ""

#         record_md = f"**_Type: {itm.name} (Record{fmt})_**\n\n"
#         headers = ["ID", "Name", "Type", "#", "Description"]
#         rows = [self._makeField(f, headers) for f in itm.__fields__.values()]
#         record_md += self._makeTable(
#             rows=rows,
#             align=[Alignment.ALIGN_RIGHT, None, None, Alignment.ALIGN_RIGHT],
#             headers=headers,
#             table=TableFormat.MarkDown
#         )
#         return f"{record_md}\n"

#     def _formatCustom(self, itm: Union[Primitive, ArrayOf, MapOf], **kwargs) -> str:
#         custom_md = "\n"
#         headers = ["Type Name", "Type Definition", "Description"]
#         field = self._makeField(itm, ld=False)
#         row = [field["name"], field["type"], field["description"]]
#         custom_md += self._makeTable(
#             rows=[row],
#             headers=headers,
#             table=TableFormat.MarkDown
#         )
#         return f"{custom_md}\n"

#     # Helper Functions
#     def _makeField(self, field: Union[ModelField, Primitive, ArrayOf, MapOf], headers: List[str] = None, ld: bool = True) -> Union[List[str], Dict[str, str]]:
#         if isinstance(field, ModelField):
#             # Field
#             opts: Options = field.field_info.extra["options"]
#             field_dict = {
#                 "id": field.field_info.extra["id"],
#                 "name": f"**{field.alias}**",
#                 "type": field.field_info.extra["type"],
#                 "options": opts.multiplicity(1, 1, True),
#                 "description": field.field_info.description,
#             }
#         else:
#             # Definition
#             opts = field.__options__
#             field_dict = {
#                 "id": "",
#                 "name": f"**{field.name}**",
#                 "type": field.data_type,
#                 "options": opts.multiplicity(1, 1, True),
#                 "description": field.description,
#             }

#         if field_dict["type"] == "MapOf":
#             field_dict["type"] += f"({opts.get('ktype', 'String')}, {opts.get('vtype', 'String')})"
#         elif field_dict["type"] == "ArrayOf":
#             field_dict["type"] += f"({opts.get('vtype', 'String')})"

#         opt_args = {} if field_dict["type"] in ("Integer", "Number") else {"check": lambda x, y: x > 0 or y > 0}
#         if multi := opts.multiplicity(**opt_args):
#             field_dict["type"] += f"{{{multi}}}"

#         field_dict["type"] += f" (%{opts.pattern}%)" if opts.pattern else ""
#         field_dict["type"] += f" /{opts.format}" if opts.format else ""
#         field_dict["type"] += " unique" if getattr(opts, "unique", False) else ""

#         if headers:
#             ordered_field = {}
#             for column in headers:
#                 col = self._table_field_headers.get(column, column)
#                 col = col if isinstance(col, str) else [k for k in col if k in field_dict][0]
#                 ordered_field[col] = field_dict.get(col, "")
#             return list(ordered_field.values()) if ld else ordered_field
#         return list(field_dict.values()) if ld else field_dict


# # Writer Functions
# def md_dump(schema: Union[str, dict, Schema], fname: str, source: str = "", comm: CommentLevels = CommentLevels.ALL, **kwargs) -> None:
#     """
#     Convert the JADN schema to MarkDown and write it to the given file
#     :param schema: Schema to convert
#     :param fname: schema file to write
#     :param source: source information
#     :param comm: comment level
#     :param kwargs: key/value args for the conversion
#     """
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoMD(schema, comm).dump(fname, source, **kwargs)


# def md_dumps(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs) -> str:
#     """
#     Convert the JADN schema to MarkDown
#     :param schema: Schema to convert
#     :param comm: comment level
#     :param kwargs: key/value args for the conversion
#     :return: MarkDown string
#     """
#     comm = comm if comm in CommentLevels else CommentLevels.ALL
#     return JADNtoMD(schema, comm).dumps(**kwargs)
