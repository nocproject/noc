# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, ReferenceField, IntField,
                                BooleanField, LongField, ListField)
import cachetools
# NOC modules
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.decorator import on_save
from noc.core.defer import call_later

id_lock = Lock()


@on_save
class ServiceProfile(Document):
    meta = {
        "collection": "noc.serviceprofiles",
        "strict": False
    }
    name = StringField(unique=True)
    description = StringField()
    # Jinja2 service label template
    card_title_template = StringField()
    # Short service code for reporting
    code = StringField()
    # FontAwesome glyph
    glyph = StringField()
    #
    show_in_summary = BooleanField(default=True)
    # Auto-assign interface profile when service binds to interface
    interface_profile = ReferenceField(InterfaceProfile)
    # Alarm weight
    weight = IntField(default=0)
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()    
    # Object id in BI
    bi_id = LongField()
    # Tags
    tags = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ServiceProfile.objects.filter(id=id).first()

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "interface_profile" in self._changed_fields:
            call_later(
                "noc.sa.models.serviceprofile.refresh_interface_profiles",
                sp_id=self.id,
                ip_id=self.interface_profile.id if self.interface_profile else None
            )


def refresh_interface_profiles(sp_id, ip_id):
    from .service import Service
    from noc.inv.models.interface import Interface
    svc = [
        x["_id"]
        for x in Service._get_collection().find(
            {"profile": sp_id}, {"_id": 1}
        )
    ]
    if not svc:
        return
    bulk = Interface._get_collection().initialize_unordered_bulk_op()
    bulk.find({
        "_id": {"$in": svc}
    }).update({
        "$set": {"profile": ip_id}
    })
