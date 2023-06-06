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
    is_protected: Optional[bool] = None
    description: Optional[str] = None
    enable_division: Optional[bool] = None
    enable_managedobject: Optional[bool] = None
    enable_managedobjectprofile: Optional[bool] = None
    enable_administrativedomain: Optional[bool] = None
    enable_authprofile: Optional[bool] = None
    enable_networksegment: Optional[bool] = None
    enable_resourcegroup: Optional[bool] = None
    enable_object: Optional[bool] = None
    enable_service: Optional[bool] = None
    enable_serviceprofile: Optional[bool] = None
    enable_subscriber: Optional[bool] = None

    _csv_fields = ["id", "name", "description"]
