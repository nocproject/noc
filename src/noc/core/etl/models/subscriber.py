# ----------------------------------------------------------------------
# SubscriberModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel
from .typing import Reference
from .subscriberprofile import SubscriberProfile


class Subscriber(BaseModel):
    id: str
    name: str
    profile: Reference["SubscriberProfile"]
    description: str | None = None
    address: str | None = None
    tech_contact_person: str | None = None
    tech_contact_phone: str | None = None

    _csv_fields = [
        "id",
        "name",
        "description",
        "profile",
        "address",
        "tech_contact_person",
        "tech_contact_phone",
    ]
