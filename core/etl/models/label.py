# ----------------------------------------------------------------------
# LabelModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class Label(BaseModel):
    id: str
    name: str
    is_protected: Optional[bool]
    description: Optional[str]
    enable_division: Optional[bool]
    enable_managedobject: Optional[bool]
    enable_managedobjectprofile: Optional[bool]
    enable_administrativedomain: Optional[bool]
    enable_authprofile: Optional[bool]
    enable_networksegment: Optional[bool]
    enable_resourcegroup: Optional[bool]
    enable_object: Optional[bool]
    enable_service: Optional[bool]
    enable_serviceprofile: Optional[bool]
    enable_subscriber: Optional[bool]
    enable_subscriberprofile: Optional[bool]

    _csv_fields = ["id", "name", "description"]
