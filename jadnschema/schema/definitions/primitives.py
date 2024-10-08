"""
JADN Primitive Types
"""
import re

from functools import partial
from typing import Any, Union
from pydantic import ConfigDict, ValidationError, model_validator
import pydantic

from jadnschema.utils.general import get_max_len, get_max_len_binary
from .definitionBase import DefinitionBase
from .options import Options
__all__ = ["Primitive", "Binary", "Boolean", "Integer", "Number", "String", "validate_format"]
Primitive = Union["Binary", "Boolean", "Integer", "Number", "String"]
primitives = ["Binary", "Boolean", "Integer", "Number", "String"]


def validate_format(cls: DefinitionBase, fmt: str, val: Any) -> Any:
    """
    Attempt to validate the format of a given Primitive type
    :param cls: Primitive type to validate
    :param fmt: format to validate against
    :param val: value to validate
    :raise Exception: invalid format
    :return: original formatted value
    """
    if re.match(r"^u\d+$", fmt):
        fun = partial(cls.__options__.validation["unsigned"], int(fmt[1:]))
    else:
        fun = cls.__options__.validation.get(fmt, None)

    if fun:
        return fun(val)
    raise ValidationError(f"{fmt} is not a valid format")


class Binary(DefinitionBase):
    """
    A sequence of octets. Length is the number of octets.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # __root__: str
    __options__ = Options(data_type="Binary")  # pylint: disable=used-before-assignment

    # Validation
    @model_validator(mode='before')
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the string as a Binary type
        :param value: value to validate
        :raise ValueError: invalid data given
        :return: original value
        """
        val = value.get(pydantic.RootModel, None)
        if fmt := cls.__options__.format:
            validate_format(cls, fmt, val)
        val_len = len(val)
        min_len = cls.__options__.minv or 0
        max_len = get_max_len_binary(cls)

        if min_len > val_len:
            raise ValidationError(f"{cls.name} is invalid, minimum length of {min_len} bytes not met")
        if max_len < val_len:
            raise ValidationError(f"{cls.name} is invalid, maximum length of {max_len} bytes exceeded")
        return value

    # class Config:
    #     arbitrary_types_allowed = True

    class Options:
        data_type = "Binary"


class Boolean(DefinitionBase):
    """
    An element with one of two values: true or false.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # __root__: bool
    __options__ = Options(data_type="Boolean")  # pylint: disable=used-before-assignment

    # class Config:
    #     arbitrary_types_allowed = True

    class Options:
        data_type = "Boolean"


class Integer(DefinitionBase):
    """
    A positive or negative whole number.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # __root__: int
    __options__ = Options(data_type="Integer")  # pylint: disable=used-before-assignment

    # Validation
    @model_validator(mode='before')
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the int as an Integer type
        :param value: value to validate
        :raise ValueError: invalid data given
        :return: original value
        """
        val = value.get(pydantic.RootModel, None)
        if fmt := cls.__options__.format:
            validate_format(cls, fmt, str(val))
        min_val = cls.__options__.minv or 0
        max_val = cls.__options__.maxv or 0

        if min_val > val:
            raise ValidationError(f"{cls.name} is invalid, minimum of {min_val} not met")
        if max_val != 0 and max_val < val:
            raise ValidationError(f"{cls.name} is invalid, maximum of {max_val} exceeded")
        return value

    # class Config:
    #     arbitrary_types_allowed = True

    class Options:
        data_type = "Integer"


class Number(DefinitionBase):
    """
    A real number.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # __root__: float
    __options__ = Options(data_type="Number")  # pylint: disable=used-before-assignment

    # Validation
    @model_validator(mode='before')
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the float as a Number type
        :param value: value to validate
        :raise ValueError: invalid data given
        :return: original value
        """
        val = value.get(pydantic.RootModel, None)
        if fmt := cls.__options__.format:
            validate_format(cls, fmt, str(val))
        min_val = cls.__options__.minf or 0
        max_val = cls.__options__.maxf or 0

        if min_val > val:
            raise ValidationError(f"{cls.name} is invalid, minimum of {min_val} not met")
        if max_val != 0 and max_val < val:
            raise ValidationError(f"{cls.name} is invalid, maximum of {max_val} exceeded")
        return value

    # class Config:
    #     arbitrary_types_allowed = True

    class Options:
        data_type = "Number"


class String(DefinitionBase):
    """
    A sequence of characters, each of which has a Unicode codepoint. Length is the number of characters.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # __root__: str
    __options__ = Options(data_type="String")  # pylint: disable=used-before-assignment

    # Validation
    @model_validator(mode='before')
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the string as a String type
        :param value: value to validate
        :raise ValueError: invalid data given
        :return: original value
        """
        val = value.get(pydantic.RootModel, None)
        if fmt := cls.__options__.format:
            validate_format(cls, fmt, val)
        val_len = len(val)
        min_len = cls.__options__.minv or 0
        max_len = get_max_len(cls)
        if min_len > val_len:
            raise ValueError(f"{cls.name} is invalid, minimum length of {min_len} characters not met")
        if max_len < val_len:
            raise ValueError(f"{cls.name} is invalid, maximum length of {max_len} characters exceeded")
        return value

    # class Config:
    #     arbitrary_types_allowed = True

    class Options:
        data_type = "String"
