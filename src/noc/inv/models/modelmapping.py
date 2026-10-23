# ---------------------------------------------------------------------
# ModelMapping model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.core.mongo.fields import PlainReferenceField


class ModelMapping(Document):
    meta = {"collection": "noc.modelmappings", "strict": False, "auto_create_index": False}

    # Vendor, as returned by get_inventory
    vendor = StringField()
    # Part number, as returned by get_inventory
    part_no = StringField()
    # Serial number ranges, if applicable
    from_serial = StringField()
    to_serial = StringField()
    model = PlainReferenceField(ObjectModel)
    is_active = BooleanField(default=True)
    description = StringField(required=False)
