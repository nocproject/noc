# ----------------------------------------------------------------------
# ContainerModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class Container(BaseModel):
    id: str
    name: str
    model: str
    path: Optional[str] = None
    addr_id: Optional[str] = None
    lon: str = ""
    lat: str = ""
    addr_text: Optional[str] = None
    adm_contact_text: Optional[str] = None
    tech_contact_text: Optional[str] = None
    billing_contact_text: Optional[str] = None

    _csv_fields = [
        "id",
        "name",
        "model",
        "path",
        "addr_id",
        "lon",
        "lat",
        "addr_text",
        "adm_contact_text",
        "tech_contact_text",
        "billing_contact_text",
    ]
