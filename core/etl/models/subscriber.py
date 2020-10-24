# ----------------------------------------------------------------------
# SubscriberModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class SubscriberModel(BaseModel):
    id: str
    name: str
    description: Optional[str]
    profile: str
    address: Optional[str]
    tech_contact_person: Optional[str]
    tech_contact_phone: Optional[str]

    _csv_fields = [
        "id",
        "name",
        "description",
        "profile",
        "address",
        "tech_contact_person",
        "tech_contact_phone",
    ]
