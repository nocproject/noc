# ----------------------------------------------------------------------
# ContainerModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class Container(BaseModel):
    id: str
    name: str
    model: str
    path: str | None = None
    addr_id: str | None = None
    lon: str = ""
    lat: str = ""
    addr_text: str | None = None
    adm_contact_text: str | None = None
    tech_contact_text: str | None = None
    billing_contact_text: str | None = None

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
