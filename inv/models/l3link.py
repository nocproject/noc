# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# L3 Link model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

from noc.core.model.decorator import on_delete, on_save
# NOC modules
from noc.lib.nosql import (Document, PlainReferenceListField,
                           StringField, DateTimeField, ListField,
                           IntField)


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
        "indexes": ["subinterfaces", "linked_objects"]
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

    def __unicode__(self):
        return u"(%s)" % ", ".join([unicode(i) for i in self.subinterfaces])

    def clean(self):
        self.linked_objects = sorted(set(i.managed_object.id for i in self.subinterfaces))
        super(L3Link, self).clean()
