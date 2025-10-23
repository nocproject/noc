# ----------------------------------------------------------------------
# L3 Link model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField, ListField, IntField

# NOC modules
from noc.core.mongo.fields import PlainReferenceListField
from noc.core.comp import smart_text
from noc.core.model.decorator import on_delete, on_save


@on_delete
@on_save
class L3Link(Document):
    """
    Network L3 links.
    Always contains a list of subinterface references
    """

    meta = {
        "collection": "noc.links",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["subinterfaces", "linked_objects"],
    }

    subinterfaces = PlainReferenceListField("inv.SubInterface")
    # List of linked objects
    linked_objects = ListField(IntField())
    # Name of discovery method or "manual"
    discovery_method = StringField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # Timestamp of last confirmation
    last_seen = DateTimeField()
    # L3 path cost
    l3_cost = IntField(default=1)

    def __str__(self):
        return "(%s)" % ", ".join([smart_text(i) for i in self.subinterfaces])

    def clean(self):
        self.linked_objects = sorted({i.managed_object.id for i in self.subinterfaces})
        super().clean()
