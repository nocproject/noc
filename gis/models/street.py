# ---------------------------------------------------------------------
# Street object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    DictField,
    BooleanField,
    DateTimeField,
    ReferenceField,
    LongField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.comp import smart_text
from .division import Division
from noc.main.models.remotesystem import RemoteSystem
from noc.core.bi.decorator import bi_sync


@bi_sync
@on_delete_check(check=[("gis.Address", "street")])
class Street(Document):
    meta = {
        "collection": "noc.streets",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["parent", "data"],
    }
    #
    parent = PlainReferenceField(Division)
    # Normalized name
    name = StringField()
    # street/town/city, etc
    short_name = StringField()
    #
    is_active = BooleanField(default=True)
    # Additional data
    # Depends on importer
    data = DictField()
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    #
    start_date = DateTimeField()
    end_date = DateTimeField()

    def __str__(self):
        if self.short_name:
            return "%s, %s" % (self.name, self.short_name)
        else:
            return self.name

    @property
    def full_path(self):
        if not self.parent:
            return ""
        r = [self.parent.full_path, smart_text(self)]
        return " | ".join(r)
