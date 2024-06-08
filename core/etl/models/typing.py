# ----------------------------------------------------------------------
# ETL-specific types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Generic, TypeVar, Any

# Third-party modules
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler


T = TypeVar("T")


class Reference(Generic[T]):
    def __init__(self, name: str, model: T, value: Any):
        self.name = name
        self.model = model
        self.value = value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, handler(str))

    @classmethod
    def validate(cls, v):
        return str(v)
