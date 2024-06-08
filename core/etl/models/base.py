# ----------------------------------------------------------------------
# BaseETLModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Iterable, Dict, _GenericAlias, _SpecialForm
from itertools import zip_longest

# Third-party modules
from pydantic import BaseModel as _BaseModel, ConfigDict
from pydantic.fields import FieldInfo

# NOC modules
from .typing import Reference


class BaseModel(_BaseModel):
    id: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # List of legacy fields in sequental order
    _csv_fields = []

    @staticmethod
    def is_reference(field: FieldInfo):
        annotation = field.annotation
        if isinstance(annotation, _GenericAlias):
            if annotation.__origin__ is Reference:
                return True
            elif isinstance(annotation.__origin__, _SpecialForm):
                for arg in annotation.__args__:
                    if isinstance(arg, _GenericAlias) and arg.__origin__ is Reference:
                        return True
        return False

    @classmethod
    def from_iter(cls, value: Iterable[Any]) -> "BaseModel":
        """
        Convert tuple or list from legacy CSV to BaseModel instance
        :param iter:
        :return:
        """
        return cls(**{fn: val for fn, val in zip_longest(cls._csv_fields.default, value) if fn})

    @classmethod
    def get_mapped_fields(cls) -> Dict[str, str]:
        def q(field: FieldInfo) -> str:
            annotation = field.annotation
            ref = None
            if isinstance(annotation, _GenericAlias):
                if annotation.__origin__ is Reference:
                    ref = annotation
                elif isinstance(annotation.__origin__, _SpecialForm):
                    for arg in annotation.__args__:
                        if isinstance(arg, _GenericAlias) and arg.__origin__ is Reference:
                            ref = arg
                            break
            if ref:
                return ref.__args__[0].__name__.lower()

        return {fn: q(f) for fn, f in cls.model_fields.items() if cls.is_reference(f)}
