# ----------------------------------------------------------------------
# ETL-specific types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Generic, TypeVar

# Third-party modules
from pydantic.fields import FieldInfo


T = TypeVar("T")


class Reference(Generic[T]):
    def __init__(self, name: str, model: T):
        self.name = name
        self.model = model

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: FieldInfo):
        return str(v)
