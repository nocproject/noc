# ---------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    IntField,
    ListField,
    DictField,
    DateTimeField,
    FloatField,
)

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.sa.models.managedobject import ManagedObject


class Discovery(Document):
    meta = {
        "collection": "noc.schedules.inv.discovery",
        "strict": False,
        "auto_create_index": False,
    }

    job_class = StringField(db_field="jcls")
    schedule = DictField()
    ts = DateTimeField(db_field="ts")
    last = DateTimeField()
    last_success = DateTimeField(db_field="st")
    last_duration = FloatField(db_field="ldur")
    last_status = StringField(db_field="ls")
    status = StringField(db_field="s")
    managed_object = ForeignKeyField(ManagedObject, db_field="key")
    data = DictField()
    traceback = DictField()
    runs = IntField()
    faults = IntField(db_field="f")
    log = ListField()

    def __str__(self):
        return "%s: %s" % (self.managed_object, self.job_class)
