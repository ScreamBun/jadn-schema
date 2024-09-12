"""
JADN to Relax-NG
"""
import json
import re
import xml.dom.minidom as md

from typing import Union
from .baseWriter import BaseWriter
from .utils import DocXML
from ..enums import CommentLevels
from ..helpers import register_writer
from ....utils import toStr
from ....schema import Schema
from ....schema.definitions import Array, ArrayOf, Choice, Enumerated, Map, MapOf, Record, Primitive
__pdoc__ = {
    "JADNtoRelaxNG.format": "File extension of the given format",
    "JADNtoRelaxNG.escape_chars": "Characters that are not supported in the schema format and need to be removed/escaped",
    "JADNtoRelaxNG.comment_multi": "Multiline comment characters; Tuple[START_CHAR, END_CHAR]",
    "JADNtoRelaxNG.comment_single": "Single line comment character",
}

FieldMap = {
    "Binary": "base64Binary",
    "Boolean": "boolean",
    "Integer": "integer",
    "Number": "float",
    "Null": "",
    "String": "string"
}
TagContents = Union[complex, dict, float, int, list, str]


"""
*******
DEPRECATED. (9/12/24)

Removed per customer request.
TODO: Eventually remove once the logic below has been verified that it is no longer needed.

*******
"""

# Conversion Class
@register_writer
class JADNtoRelaxNG(BaseWriter):
    format: str = "rng"
    comment_multi = ("<!--", "-->")
    comment_single = ""

    def dumps(self, **kwargs) -> str:
        # Make initial tree
        root_kwargs = {
            "root_tag": "grammar",
            "xmlns": "http://relaxng.org/ns/structure/1.0",
            "datatypeLibrary": "http://www.w3.org/2001/XMLSchema-datatypes"
        }
        doc, tag = DocXML(self.makeHeader(), **root_kwargs).context()

        with tag("start"):
            with tag("choice"):
                export_names = self._schema.info.exports.schema()
                exports = [t.name for t in self._schema.types.values() if t.data_type == "Record" and t.name in export_names]
                # exports = self._info.exports
                # TODO: What should be here??
                for e in exports:
                    with tag("element", name="message"):
                        self._fieldType(e, tag)

        self._makeStructures(tag=tag)
        return doc.getvalue(True)

    def makeHeader(self) -> str:
        """
        Create the header for the schema
        :return: header for schema
        """
        header_regex = re.compile(r"(^\"|\"$)")
        header = []
        info = self._schema.info.schema()
        for k, v in info.items():
            header.append(f"<!-- meta: {k} - {header_regex.sub('', json.dumps(v))} -->")
        return "\n".join(header) + "\n"

    # Structure Formats
    def _formatArray(self, itm: Array, **kwargs) -> None:  # TODO: what should this do??
        tag: DocXML.tag = kwargs["tag"]
        type_opts = {"type": itm.data_type}
        if o := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = o

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(self._formatComment(itm.description, jadn_opts=type_opts))
            with tag("interleave"):
                for field in itm.__fields__.values():
                    field_opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
                    if o := field.field_info.extra["options"].dict(exclude_unset=True):
                        field_opts["options"] = o
                    tag_opts = {
                        "tag_name": "element",
                        "name": self.formatStr(field.alias)
                    }
                    com = self._formatComment(field.field_info.description, jadn_opts=field_opts)
                    if field.required:
                        with tag(**tag_opts) as p:
                            p.comment(com)
                            self._fieldType(field.field_info.extra["type"], tag)
                    else:
                        with tag("optional"):
                            with tag(**tag_opts) as p:
                                p.comment(com)
                                self._fieldType(field.field_info.extra["type"], tag)

    def _formatArrayOf(self, itm: ArrayOf, **kwargs) -> None:  # TODO: what should this do??
        tag: DocXML.tag = kwargs["tag"]
        type_opts = {"type": itm.data_type}
        if o := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = o

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(self._formatComment(itm.description, jadn_opts=type_opts))
            with tag("oneOrMore" if type_opts["options"] and len(type_opts["options"]) > 0 else "zeroOrMore"):
                self._fieldType(itm.__options__.get("vtype", "string"), tag)

    def _formatChoice(self, itm: Choice, **kwargs) -> None:
        tag: DocXML.tag = kwargs["tag"]
        type_opts = {"type": itm.data_type}
        if o := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = o

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(self._formatComment(itm.description, jadn_opts=type_opts))
            with tag("choice"):
                for field in itm.__fields__.values():
                    n = self.formatStr(field.alias or f"Unknown_{self.formatStr(itm.name)}_{field.field_info.extra['id']}")
                    field_opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
                    if o := field.field_info.extra["options"].dict(exclude_unset=True):
                        field_opts["options"] = o

                    with tag("element", name=n) as p:
                        p.comment(self._formatComment(field.field_info.description, jadn_opts=field_opts))
                        self._fieldType(field.field_info.extra["type"], tag)

    def _formatEnumerated(self, itm: Enumerated, **kwargs) -> None:
        tag: DocXML.tag = kwargs["tag"]
        type_opts = {"type": itm.data_type}
        if o := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = o

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(self._formatComment(itm.description, jadn_opts=type_opts))
            with tag("choice"):
                for field in itm.__enums__:
                    val = field.value
                    field_opts = {"field": val.extra["id"]}
                    p = tag("value", self.formatStr(val.default or f"Unknown_{self.formatStr(val.alias)}_{val.extra['id']}"))
                    p.comment(self._formatComment(val.description, jadn_opts=field_opts))

    def _formatMap(self, itm: Map, **kwargs) -> None:
        tag: DocXML.tag = kwargs["tag"]
        type_opts = {"type": itm.data_type}
        if o := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = o

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(self._formatComment(itm.description, jadn_opts=type_opts))
            with tag("interleave"):
                for field in itm.__fields__.values():
                    field_opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
                    if o := field.field_info.extra["options"].dict(exclude_unset=True):
                        field_opts["options"] = o

                    tag_opts = {
                        "tag_name": "element",
                        "name": self.formatStr(field.alias)
                    }
                    com = self._formatComment(field.field_info.description, jadn_opts=field_opts)
                    if field.required:
                        with tag(**tag_opts) as p:
                            p.comment(com)
                            self._fieldType(field.field_info.extra["type"], tag)
                    else:
                        with tag("optional"):
                            with tag(**tag_opts) as p:
                                p.comment(com)
                                self._fieldType(field.field_info.extra["type"], tag)

    def _formatMapOf(self, itm: MapOf, **kwargs) -> None:
        tag: DocXML.tag = kwargs["tag"]
        type_opts = {"type": itm.data_type}
        if o := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = o

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(self._formatComment(itm.description, jadn_opts=type_opts))
            with tag("interleave"):
                key_type = self._schema.types.get(itm.__options__.get("ktype"))
                if key_type.data_type in ("Choice", "Enumerated", "Map", "Record"):
                    if key_type.data_type == "Enumerated":
                        keys = [f.name for f in key_type.__enums__]
                    else:
                        keys = [f.alias for f in key_type.__fields__.values()]
                else:
                    raise TypeError(f"Invalid MapOf definition for {itm.name}")

                value_type = itm.__options__.get("vtype", "String")
                for k in keys:
                    with tag("optional"):
                        with tag(tag_name="element", name=self.formatStr(k)):
                            self._fieldType(value_type, tag)

    def _formatRecord(self, itm: Record, **kwargs) -> None:
        tag: DocXML.tag = kwargs["tag"]
        type_opts = {"type": itm.data_type}
        if o := itm.__options__.dict(exclude_unset=True):
            type_opts["options"] = o

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(self._formatComment(itm.description, jadn_opts=type_opts))
            with tag("interleave"):
                for field in itm.__fields__.values():
                    field_opts = {"type": field.field_info.extra["type"], "field": field.field_info.extra["id"]}
                    if o := field.field_info.extra["options"].dict(exclude_unset=True):
                        field_opts["options"] = o

                    tag_opts = {
                        "tag_name": "element",
                        "name": self.formatStr(field.alias)
                    }
                    com = self._formatComment(field.field_info.description, jadn_opts=field_opts)
                    if field.required:
                        with tag(**tag_opts) as p:
                            p.comment(com)
                            self._fieldType(field.field_info.extra["type"], tag)
                    else:
                        with tag("optional"):
                            with tag(**tag_opts) as p:
                                p.comment(com)
                                self._fieldType(field.field_info.extra["type"], tag)

    def _formatCustom(self, itm: Union[Primitive, ArrayOf, MapOf], **kwargs) -> None:
        tag: DocXML.tag = kwargs["tag"]
        com = itm.description if itm.description else ""
        if o := itm.__options__.dict(exclude_unset=True):
            com += f" #jadn_opts:{json.dumps({'options': o})}"

        with tag("define", name=self.formatStr(itm.name)) as t:
            t.comment(com)
            self._fieldType(itm.data_type, tag)

    # Helper Functions
    def _formatPretty(self, xml) -> str:
        """
        Format the XML in a human-readable format
        :param xml: XML string to format
        :return: formatted XML
        """
        rtn_xml = "\n".join([line for line in md.parseString(xml).toprettyxml(indent=self._indent).split("\n") if line.strip()])
        return re.sub(r"^<\?xml.*?\?>\n", "", rtn_xml)

    def _formatTag(self, tag: str, contents: TagContents = "", com="", **kwargs) -> str:
        """
        Format a tag using the given information
        :param tag: tag name
        :param contents: contents of the tag
        :param com: comment to add with the tag
        :param kwargs: key/value attributes of the tag
        :return: formatted tag
        """
        ign = ["", None]
        attrs = "".join([f" {k}={json.dumps(v)}" for k, v in kwargs.items()])

        if contents in ign and com in ign:
            elm = f"<{tag}{attrs}/>"

        else:
            elm = f"<{tag}{attrs}>"
            if com != "" and re.match(r"^<!--.*?-->", com):
                elm += com
            elif com != "":
                elm += f"<!--{self._formatComment(com).strip()}-->"

            if isinstance(contents, (str, int, float, complex)):
                elm += toStr(contents)
            elif isinstance(contents, list):
                elm += "".join(itm for itm in contents if isinstance(itm, str))
            elif isinstance(contents, dict):
                elm += "".join(self._formatTag(k, v) for k, v in contents.items())

            else:
                print(f"unprepared type: {type(contents)}")

            elm += f"</{tag}>"

        return elm

    def _fieldType(self, f: str, tag: DocXML.tag) -> DocXML.Tag:
        """
        Determines the field type for the schema
        :param f: current type
        """
        if f in self._customFields:
            return tag("ref", name=self.formatStr(f))
        if f in FieldMap:
            rtn = self.formatStr(FieldMap.get(f, f))
            return tag("text") if rtn == "" else tag("data", type=rtn)
        return tag("text")


# Writer Functions
def relax_dump(schema: Union[str, dict, Schema], fname: str, source: str = "", comm: CommentLevels = CommentLevels.ALL, **kwargs) -> None:
    """
    Convert the JADN schema to Relax-NG and write it to the given file
    :param schema: Schema to convert
    :param fname: schema file to write
    :param source: source information
    :param comm: comment level
    :param kwargs: key/value args for the conversion
    """
    comm = comm if comm in CommentLevels else CommentLevels.ALL
    return JADNtoRelaxNG(schema, comm).dump(fname, source, **kwargs)


def relax_dumps(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs) -> str:
    """
    Convert the JADN schema to Relax-NG
    :param schema: Schema to convert
    :param comm: comment level
    :param kwargs: key/value args for the conversion
    :return: Relax-NG string
    """
    comm = comm if comm in CommentLevels else CommentLevels.ALL
    return JADNtoRelaxNG(schema, comm).dumps(**kwargs)
