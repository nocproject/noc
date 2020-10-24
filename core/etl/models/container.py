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


class ContainerModel(BaseModel):
    id: str
    name: str
    model: str
    path: Optional[str]
    addr_id: Optional[str]
    lon: str
    lat: str
    addr_text: Optional[str]
    adm_contact_text: Optional[str]
    tech_contact_text: Optional[str]
    billing_contact_text: Optional[str]

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
