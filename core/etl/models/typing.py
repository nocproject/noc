# ----------------------------------------------------------------------
# ETL-specific types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Generic, TypeVar, Any, Optional, Union

# Third-party modules
from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler, BaseModel


T = TypeVar("T")


class RemoteReference(BaseModel):
    id: str
    remote_system: Optional[str]


class ETLMapping(BaseModel):
    value: str
    scope: str
    remote_id: Optional[str] = None


class Reference(Generic[T]):
    def __init__(self, name: str, model: T, value: Any, remote_system: Optional[str] = None):
        self.name = name
        self.model = model
        self.value = value
        self.remote_system = remote_system

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(Union[str, RemoteReference, ETLMapping])
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, (RemoteReference, ETLMapping)):
            return v
        return str(v)
