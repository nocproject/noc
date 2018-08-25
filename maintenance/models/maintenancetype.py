# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MaintenanceType
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField


class MaintenanceType(Document):
    meta = {
        "collection": "noc.maintenancetype",
        "strict": False,
        "auto_create_index": False,
        "legacy_collections": ["noc.maintainancetype"]
    }

    name = StringField(unique=True)
    description = StringField()
    suppress_alarms = BooleanField()
    card_template = StringField()

    def __unicode__(self):
        return self.name
