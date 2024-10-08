"""
JADN Definition BaseModel
Customized from `jadnschema.schema.baseModel.BaseModel`
"""
from copy import deepcopy
from enum import Enum
from typing import Any, ClassVar
from pydantic import ConfigDict, create_model
import pydantic
# from pydantic._internal._model_construction import ModelMetaclass
from .options import Options
from .field import getFieldSchema, getFieldType
from ..consts import SELECTOR_TYPES, STRUCTURED_TYPES, FIELD_TYPES
from ..baseModel import BaseModel
from ...utils import classproperty, ellipsis_str
__pdoc__ = {
    "DefinitionBase.name": "The definition's valid schema name",
    "DefinitionBase.description": "The definition's description",
    "DefinitionBase.data_type": "The definition's base datatype"
}


# class DefinitionMeta(ModelMetaclass):
#     def __new__(mcs, name, bases, attrs, **kwargs):
#         base_opts = [b.__options__ for b in reversed(bases) if issubclass(b, BaseModel) and b != BaseModel]
#         opts = Options(
#             *base_opts,
#             attrs.pop("__options__", None), attrs.pop("Options", None),
#             kwargs.pop("__options__", None), kwargs.pop("Options", None),
#             getattr(mcs, "__options__", None), getattr(mcs, "Options", None),
#         )
#         new_namespace = {
#             **attrs,
#             **kwargs,
#             "__options__": opts,
#         }
#         cls = super().__new__(mcs, name, bases, new_namespace)
#         base_names = [b.__name__ for b in bases]
#         for idx, (field, opts) in enumerate(cls.model_fields.items()):
#             if field != pydantic.RootModel:
#                 opts.field_info.extra["parent"] = cls
#                 field_opts = opts.field_info.extra["options"]
#                 field_opts.setdefault("name", f"{name}.{opts.alias}")
#                 field_opts.setdefault("data_type", getFieldType(opts))
#                 opts.field_info.extra.setdefault("id", idx)
#                 if not opts.required and field_opts.minc != 0 and "Choice" not in base_names:
#                     field_opts.minc = 0
#         return cls


# class DefinitionBase(BaseModel, metaclass=DefinitionMeta):
class DefinitionBase(BaseModel):
    __options__: ClassVar[Options]

    def __str__(self):
        cls = self.__class__
        mro = [c for c in cls.__mro__ if not c.__name__ == cls.__name__][0]
        data = self.model_dump_json(exclude_none=True)
        return f"{self.name}({mro.__name__}: {ellipsis_str(data)})"

    # Pydantic overrides
    @classmethod
    def schema(cls) -> list:
        """
        Format the definition to valid JADN schema format
        :return: formatted JADN
        """
        mro = [c for c in cls.__mro__ if not c.__name__ == cls.__name__][0]
        schema = [cls.name, mro.__name__, cls.__options__.schema(), (cls.__doc__ or "").strip()]
        if cls.model_fields and pydantic.RootModel not in cls.model_fields:
            fields = []
            for opt in cls.model_fields.values():
                fields.append(getFieldSchema(opt))
            schema.append(fields)
        return schema

    # Custom Methods
    @classmethod
    def is_enum(cls) -> bool:
        """
        Determine if the definition is an enumerated type
        :return: True/False if the definition is an enumerated type
        """
        for base in cls.__mro__:
            if base.__name__ == "Enumerated":
                return True
        return False

    @classmethod
    def is_structure(cls) -> bool:
        """
        Determine if the definition is a structure type
        `Array`, `ArrayOf`, `Map`, `MapOf`, & `Record` are structure types
        :return: True/False if the definition is a structure type
        """
        for base in cls.__mro__:
            if base.__name__ in STRUCTURED_TYPES:
                return True
        return False

    @classmethod
    def is_selector(cls) -> bool:
        """
        Determine if the definition is a selector type
        `Enumerated` & `Choice` are selector types
        :return: True/False if the definition is a selector type
        """
        for base in cls.__mro__:
            if base.__name__ in SELECTOR_TYPES:
                return True
        return False

    @classmethod
    def has_fields(cls) -> bool:
        """
        Determine if the definition has fields
        `Enumerated`, `Choice`, `Array`, `Map`, & `Record` should have defined fields
        :return: True/False if the definition has fields
        """
        for base in cls.__mro__:
            if base.__name__ in FIELD_TYPES:
                return True
        return False

    # Helpers
    @classmethod
    def expandCompact(cls, value: Any) -> Any:
        if isinstance(value, dict) and cls.model_fields:
            rtn = {}
            for field in cls.model_fields.values():
                f_id = field.field_info.extra["id"]
                if f_id in value:
                    rtn[field.alias] = field.type_.expandCompact(value[f_id])
            return rtn
        return value

    @classproperty
    def name(cls) -> str:  
        """The definition's valid schema name"""
        return cls.__options__.name or cls.__name__

    @classproperty
    def description(cls) -> str:  
        """The definition's description"""
        return cls.__doc__

    @classproperty
    def data_type(cls) -> str:  
        """The definition's base datatype"""
        return cls.__options__.data_type

    @classmethod
    def enumerated(cls) -> "Enumerated": 
        """
        Convert the given class to an 'Enumerated' class if applicable
        :return: converted Enumerated class object
        """
        model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
        
        if cls.data_type in ("Binary", "Boolean", "Integer", "Number", "Null", "String"):
            raise TypeError(f"{cls.name} cannot be extended as an enumerated type")

        if cls.data_type == "Enumerated":  # pylint: disable=comparison-with-callable
            return cls

        from .structures import Enumerated  # pylint: disable=import-outside-toplevel
        name = f"Enum-{cls.name}"
        values = {}
        for k, v in cls.model_fields.items():
            values[k] = deepcopy(v.field_info)
            values[k].default = k

        cls_kwargs = dict(
            __name__=name,
            __doc__=f"Derived Enumerated from {cls.name}",
            __enums__=Enum("__enums__", values),
            __options__=Options(cls.__options__, name=name)
        )
        return create_model(name, __base__=Enumerated, __cls_kwargs__=cls_kwargs)

    # class Config:
    #     arbitrary_types_allowed = True
    #     from_attributes = True