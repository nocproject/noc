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
from .typing import Reference
from .subscriberprofile import SubscriberProfile


class Subscriber(BaseModel):
    id: str
    name: str
    profile: Reference["SubscriberProfile"]
    description: Optional[str] = None
    address: Optional[str] = None
    tech_contact_person: Optional[str] = None
    tech_contact_phone: Optional[str] = None

    _csv_fields = [
        "id",
        "name",
        "description",
        "profile",
        "address",
        "tech_contact_person",
        "tech_contact_phone",
    ]
