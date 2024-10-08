"""
JADN definition field helpers
"""
from typing import Any, ForwardRef, Optional, Union, get_args, get_origin
from pydantic import Field as pydanticField
from pydantic.v1.typing import NoArgAnyCallable
from pydantic.v1.fields import ModelField
from .options import Options


def getFieldType(field: ModelField) -> str:
    """
    Get the base type of the field
    :param field: the field to get het base type
    :return: base field type
    """
    ref = field.type_
    if isinstance(ref, ForwardRef):
        ref = getattr(ref, "__forward_arg__", ref)
        if not isinstance(ref, str):
            return getattr(ref, "name", ref.__name__)
    if get_origin(ref) is Union:
        args = [r for r in get_args(ref) if not issubclass(r, type(None))]
        if len(args) > 1:
            raise TypeError(f"Field {field.alias} is not correctly typed")
        return getattr(args[0], "name", ref)
    return getattr(ref, "name", ref)


def getFieldSchema(field: ModelField) -> list:
    """
    Format the definition to valid JADN schema format
    :param field: field to get the JADN schema
    :return: formatted JADN
    """
    field_extra = field.field_info.extra
    parent = field_extra.get("parent")
    schema = [field_extra.get("id"), field.alias]

    if parent.has_fields():
        opts = field_extra.get("options")
        schema.append(getFieldType(field))
        schema.append(opts.schema())
    schema.append(field.field_info.description or "")
    return schema


def Field(default: Any = None, *, default_factory: Optional[NoArgAnyCallable] = None, alias: str = None,
    title: str = None, description: str = None, exclude: Union['AbstractSetIntStr', 'MappingIntStrAny', Any] = None,
    include: Union['AbstractSetIntStr', 'MappingIntStrAny', Any] = None, const: bool = None, gt: float = None,
    ge: float = None, lt: float = None, le: float = None, multiple_of: float = None, allow_inf_nan: bool = None,
    max_digits: int = None, decimal_places: int = None, min_items: int = None, max_items: int = None,
    unique_items: bool = None, min_length: int = None, max_length: int = None, allow_mutation: bool = True,
    regex: str = None, discriminator: str = None, repr: bool = True, **extra: Any) -> pydanticField:
    """
    Used to provide extra information about a field, either for the model schema or complex validation. Some arguments
    apply only to number fields (``int``, ``float``, ``Decimal``) and some apply only to ``str``.

    :param default: since this is replacing the field’s default, its first argument is used
      to set the default, use ellipsis (``...``) to indicate the field is required
    :param default_factory: callable that will be called when a default value is needed for this field
      If both `default` and `default_factory` are set, an error is raised.
    :param alias: the public name of the field
    :param title: can be any string, used in the schema
    :param description: can be any string, used in the schema
    :param exclude: exclude this field while dumping.
      Takes same values as the ``include`` and ``exclude`` arguments on the ``.dict`` method.
    :param include: include this field while dumping.
      Takes same values as the ``include`` and ``exclude`` arguments on the ``.dict`` method.
    :param const: this field is required and *must* take it's default value
    :param gt: only applies to numbers, requires the field to be "greater than". The schema
      will have an ``exclusiveMinimum`` validation keyword
    :param ge: only applies to numbers, requires the field to be "greater than or equal to". The
      schema will have a ``minimum`` validation keyword
    :param lt: only applies to numbers, requires the field to be "less than". The schema
      will have an ``exclusiveMaximum`` validation keyword
    :param le: only applies to numbers, requires the field to be "less than or equal to". The
      schema will have a ``maximum`` validation keyword
    :param multiple_of: only applies to numbers, requires the field to be "a multiple of". The
      schema will have a ``multipleOf`` validation keyword
    :param allow_inf_nan: only applies to numbers, allows the field to be NaN or infinity (+inf or -inf),
        which is a valid Python float. Default True, set to False for compatibility with JSON.
    :param max_digits: only applies to Decimals, requires the field to have a maximum number
      of digits within the decimal. It does not include a zero before the decimal point or trailing decimal zeroes.
    :param decimal_places: only applies to Decimals, requires the field to have at most a number of decimal places
      allowed. It does not include trailing decimal zeroes.
    :param min_items: only applies to lists, requires the field to have a minimum number of
      elements. The schema will have a ``minItems`` validation keyword
    :param max_items: only applies to lists, requires the field to have a maximum number of
      elements. The schema will have a ``maxItems`` validation keyword
    :param unique_items: only applies to lists, requires the field not to have duplicated
      elements. The schema will have a ``uniqueItems`` validation keyword
    :param min_length: only applies to strings, requires the field to have a minimum length. The
      schema will have a ``maximum`` validation keyword
    :param max_length: only applies to strings, requires the field to have a maximum length. The
      schema will have a ``maxLength`` validation keyword
    :param allow_mutation: a boolean which defaults to True. When False, the field raises a TypeError if the field is
      assigned on an instance.  The BaseModel Config must set validate_assignment to True
    :param regex: only applies to strings, requires the field match against a regular expression
      pattern string. The schema will have a ``pattern`` validation keyword
    :param discriminator: only useful with a (discriminated a.k.a. tagged) `Union` of sub models with a common field.
      The `discriminator` is the name of this common field to shorten validation and improve generated schema
    :param repr: show this field in the representation
    :param **extra: any additional keyword arguments will be added as is to the schema
    """
    extra["options"] = Options(extra.get("options"))
    return pydanticField(
        default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        exclude=exclude,
        include=include,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_items=min_items,
        max_items=max_items,
        unique_items=unique_items,
        min_length=min_length,
        max_length=max_length,
        allow_mutation=allow_mutation,
        regex=regex,
        discriminator=discriminator,
        repr=repr,
        **extra,
    )
