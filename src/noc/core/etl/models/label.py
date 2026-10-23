# ----------------------------------------------------------------------
# LabelModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Literal

# NOC modules
from .base import BaseModel


class RegexMatch(BaseModel):
    regexp: str
    scope: Literal["managedobject_name", "managedobject_address", "managedobject_description"]


class Label(BaseModel):
    id: str
    name: str
    is_protected: bool | None = None
    description: str | None = None
    match_regex: RegexMatch | None = None
    enable_division: bool | None = None
    enable_managedobject: bool | None = None
    enable_managedobjectprofile: bool | None = None
    enable_administrativedomain: bool | None = None
    enable_authprofile: bool | None = None
    enable_networksegment: bool | None = None
    enable_resourcegroup: bool | None = None
    enable_object: bool | None = None
    enable_service: bool | None = None
    enable_serviceprofile: bool | None = None
    enable_subscriber: bool | None = None
    expose_metric: bool = False
    expose_datastream: bool = False
    expose_alarm: bool = False

    _csv_fields = ["id", "name", "description"]
