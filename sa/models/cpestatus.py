# ----------------------------------------------------------------------
# CPEStatus
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from .managedobject import ManagedObject


class CPEStatus(Document):
    meta = {
        "collection": "cpestatuses",
        "strict": False,
        "auto_create_index": False,
        "indexes": [("managed_object", "interface")],
    }

    managed_object = ForeignKeyField(ManagedObject)
    interface = StringField()
    local_id = StringField()
    global_id = StringField(unique=True)
    name = StringField()
    status = StringField()
    type = StringField()
    vendor = StringField()
    model = StringField()
    version = StringField()
    serial = StringField()
    ip = StringField()
    mac = StringField()
    modulation = StringField()
    description = StringField()
    location = StringField()
    distance = IntField()

    def __str__(self):
        return self.global_id
