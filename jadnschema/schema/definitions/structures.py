"""
JADN Structure Types
"""
from enum import Enum, EnumMeta
from typing import Any, ClassVar, Optional, Union
from pydantic import Extra, root_validator
from pydantic.utils import GetterDict

from jadnschema.schema.info import Config
from jadnschema.utils.general import get_max_v

from .definitionBase import DefinitionBase, DefinitionMeta
from .options import Options  # pylint: disable=unused-import
from .primitives import validate_format

__all__ = ["Array", "ArrayOf", "Choice", "Enumerated", "Map", "MapOf", "Record"]


# Meta Classes
class OptionalFieldsMeta(DefinitionMeta):
    def __new__(mcs, name, bases, attrs, **kwargs):  # pylint: disable=bad-classmethod-argument
        annotations = attrs.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = Optional[annotations[field]]
        new_namespace = {
            **attrs,
            "__annotations__": annotations
        }
        return super().__new__(mcs, name, bases, new_namespace, **kwargs)


class EnumeratedMeta(DefinitionMeta):
    def __new__(mcs, name, bases, attrs, **kwargs):  # pylint: disable=bad-classmethod-argument
        base_enums = list(filter(None, [
            *[getattr(b, "__enums__", None) for b in reversed(bases) if issubclass(b, DefinitionBase) and b != DefinitionBase],
            attrs.pop("__enums__", None), attrs.pop("Values", None),
            kwargs.pop("__enums__", None), kwargs.pop("Values", None),
            getattr(mcs, "__enums__", None), getattr(mcs, "Values", None),
        ]))
        enums = {}
        for enum in base_enums:
            if isinstance(enum, (Enum, EnumMeta)):
                enums.update({e.name: e.value for e in enum})
            else:
                enums.update({k: getattr(enum, k) for k in vars(enum) if not k.startswith("_")})
        new_namespace = {
            **attrs,
            "__enums__": Enum(name, enums)
        }
        return super().__new__(mcs, name, bases, new_namespace, **kwargs)


# Structure Classes
class Array(DefinitionBase):
    """
    An ordered list of labeled fields with positionally-defined semantics.
    Each field has a position, label, and type.
    """
    # __root__: Union[set, str, tuple]
    __options__ = Options(data_type="Array")  # pylint: disable=used-before-assignment

    @root_validator(pre=True)
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the data as an Array type
        :param value: data to validate
        :raise ValueError: invalid data given
        :return: original data
        """

        if isinstance(value, (GetterDict)):
            value = value._obj

            if fmt := cls.__options__.format:
                print(f"Array format: {value}")
                validate_format(cls, fmt, value)

                # special case : format MTI3LjAuMC4x/30 to [MTI3LjAuMC4x, 30]
                if isinstance(value, (list, tuple)):
                    value = value
                elif '/' in value:
                    val = value.split("/")
                    value = []
                    for i in val:
                        if i.isdigit():
                            value.append(int(i))
                        else:
                            value.append(i)
                else:
                    value = [value]
    
            # PASS : {ipv4-addr: MTI3LjAuMC4x, prefix-length: 30}
            value = {k:v for k,v in zip(cls.__fields__.keys(), value)}

            minProps = cls.__options__.minv or 0
            maxProps = get_max_v(cls)

            if len(value) < minProps:
                raise ValueError("minimum property count not met")

            if len(value) > maxProps:
                raise ValueError("maximum property count exceeded")

        return value

    class Options:
        data_type = "Array"


class ArrayOf(DefinitionBase):
    """
    A collection of fields with the same semantics.
    Each field has type vtype.
    Ordering and uniqueness are specified by a collection option.
    """
    __root__: Union[set, str, tuple]
    __options__ = Options(data_type="ArrayOf")  # pylint: disable=used-before-assignment

    @root_validator(pre=True)
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the data as an ArrayOf type
        :param value: data to validate
        :raise ValueError: invalid data given
        :return: original data
        """
        val = value.get("__root__", None)

        # check format: within []
        if not isinstance(val, list):
            raise ValueError("Expected ArrayOf values")


        minProps = cls.__options__.minv or 0
        maxProps = get_max_v(cls)

        if len(val) < minProps:
            raise ValueError("minimum property count not met")

        if len(val) > maxProps:
            raise ValueError("maximum property count exceeded")

        vtype = cls.__options__.vtype
        if not vtype or vtype is None:
            raise ValueError(f"ValueType of `{vtype}` is unknown")   
                
        # Check known type value objects
        if val_cls := cls.__config__.types.get(vtype):
            if isinstance(val, list):
               for v in val:
                    try:
                        val_cls.validate(v) 
                    except:
                        raise ValueError(f"`{v}` is not a valid vtype `{vtype}`")
                        
        else:
            # Else, check for primitives 
            if isinstance(val, list):
               for v in val:
                if not isinstance(v, (int, float, str)):
                    raise ValueError(f"Value of `{v}` is not valid within the schema") 
            else:
                if not isinstance(v, (int, float, str)):
                    raise ValueError(f"Value of `{v}` is not valid within the schema") 

        return value

    # Helpers
    @classmethod
    def expandCompact(cls, value: Any) -> Any:
        if all(str(v).isdigit() for v in value):
            vtype = cls.__options__.vtype
            if val_cls := cls.__config__.types.get(vtype):
                return [val_cls.expandCompact(v) for v in value]
            raise ValueError(f"ValueType of `{vtype}` is not valid within the schema")
        return value

    class Options:
        data_type = "ArrayOf"


class Choice(DefinitionBase, metaclass=OptionalFieldsMeta):
    """
    A discriminated union: one type selected from a set of named or labeled types.
    """
    # __root__: Union[set, str, tuple]
    __options__ = Options(data_type="Choice")  # pylint: disable=used-before-assignment

    @root_validator(pre=True)
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the data as an Choice type
        :param value: data to validate
        :raise ValueError: invalid data given
        :return: original data
        """

        # If primitive directly in choice
        if val := value.get("__root__"):

            if len(value.keys()) > 1:
                raise ValueError(f"Choice type should only have one field, not {len(value.keys())}")
            
            for v in cls.__fields__.keys():
                if val == v:
                    return value
                
            raise ValueError(f"Value `{val}` is not valid for {cls.name}")
                
        # Else object found, regular pydantic validation
        else:
            return value
        

    class Options:
        data_type = "Choice"

    class Config:
        extra = Extra.allow


class Enumerated(DefinitionBase, metaclass=EnumeratedMeta):  # pylint: disable=invalid-metaclass
    """
    A vocabulary of items where each item has an id and a string value.
    """
    __root__: Union[int, str]
    __options__ = Options(data_type="Enumerated")  # pylint: disable=used-before-assignment
    __enums__: ClassVar[Enum]

    # Pydantic overrides
    @classmethod
    def schema(cls) -> list:
        mro = [c for c in cls.__mro__ if not c.__name__ == cls.__name__][0]
        return [cls.name, mro.__name__, cls.__options__.schema(), (cls.__doc__ or "").strip(),
                [[v.value.extra["id"], v.value.default, v.value.description or ""] for v in cls.__enums__]]

    # Validation
    @root_validator(pre=True)
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the value as an Enumerated type
        :param value: value to validate
        :raise ValueError: invalid data given
        :return: original value
        """
        val = value.get("__root__", None)
        if cls.__options__.id:
            for v in cls.__enums__:
                if val == v.value.extra.get("id", None):
                    return value
        else:
            for v in cls.__enums__:
                if val == v.name:
                    return value
        raise ValueError(f"Value `{val}` is not valid for {cls.name}")

    # Helpers
    @classmethod
    def expandCompact(cls, value: int) -> str:
        if isinstance(value, int) and cls.__enums__:
            for field in cls.__enums__:
                if field.value.extra["id"] == value:
                    return field.value.default
        return str(value)

    class Options:
        data_type = "Enumerated"


class Map(DefinitionBase):
    """
    An unordered map from a set of specified keys to values with semantics bound to each key.
    Each key has an id and name or label, and is mapped to a value type.
    """
    # __root__: dict
    __options__ = Options(data_type="Map")  # pylint: disable=used-before-assignment

    # Validation
    @root_validator(pre=True)
    def validate_data(cls, value: dict):  # pylint: disable=no-self-argument

        schema_keys = cls.__fields__.keys()
        for msg_k, msg_v in value.items():
            if msg_k not in schema_keys:
                raise ValueError(f"KeyType of `{msg_k}` is not valid within the schema") 

        minProps = cls.__options__.minv or 0
        maxProps = get_max_v(cls)

        if len(value) < minProps:
            raise ValueError("minimum property count not met")

        if len(value) > maxProps:
            raise ValueError("maximum property count exceeded")

        return value

    class Config:
        extra = Extra.allow

    class Options:
        data_type = "Map"
        minv = 1


class MapOf(DefinitionBase):
    """
    An unordered map from a set of keys of the same type to values with the same semantics.
    Each key has key type ktype, and is mapped to value type vtype.
    """
    __root__: Union[set, str, tuple]
    __options__ = Options(data_type="MapOf")  # pylint: disable=used-before-assignment

    @root_validator(pre=True)
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the data as a MapOf type
        :param value: data to validate
        :raise ValueError: invalid data given
        :return: original data
        """

        val = value.get("__root__", None)

        minProps = cls.__options__.minv or 0
        maxProps = get_max_v(cls)

        if len(val) < minProps:
            raise ValueError("minimum property count not met")

        if len(val) > maxProps:
            raise ValueError("maximum property count exceeded")      

        ktype = cls.__options__.ktype
        k_cls = cls.__config__.types.get(ktype) 
        if not ktype or ktype is None:
            raise ValueError(f"KeyType of `{ktype}` is not valid within the schema")   

        vtype = cls.__options__.vtype
        v_cls = cls.__config__.types.get(vtype)
        if not vtype or vtype is None:
            raise ValueError(f"ValueType of `{vtype}` is not valid within the schema")                

        for k, v in val.items():
            try:
                k_cls.validate(k) 
            except:
                raise ValueError(f"`{k}` is not a valid ktype`{ktype}`")     
            try:
                v_cls.validate(v)
            except:
                raise ValueError(f"`{v}` is not a valid vtype `{vtype}`")
    
        return value

    # Helpers
    @classmethod
    def expandCompact(cls, value: dict) -> dict:
        # TODO: finish compact to verbose
        return value

    class Config:
        extra = Extra.allow

    class Options:
        data_type = "MapOf"


class Record(DefinitionBase):
    """
    An ordered map from a list of keys with positions to values with positionally-defined semantics.
    Each key has a position and name, and is mapped to a value type. Represents a row in a spreadsheet or database table.
    """
    #__root__: dict
    __options__ = Options(data_type="Record")  # pylint: disable=used-before-assignment

    @root_validator(pre=True)
    def validate_data(cls, value: dict) -> dict:  # pylint: disable=no-self-argument
        """
        Pydantic validator - validate the data as a Record type
        :param value: data to validate
        :raise ValueError: invalid data given
        :return: original data
        """
                
        minProps = cls.__options__.minv or 0
        maxProps = get_max_v(cls)

        if len(value) < minProps:
            raise ValueError("minimum property count not met")

        if len(value) > maxProps:
            raise ValueError("maximum property count exceeded")

        return value

    class Config:
        extra = Extra.forbid

    class Options:
        data_type = "Record"
