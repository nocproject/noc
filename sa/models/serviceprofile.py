# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Profile
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ReferenceField, IntField
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.model.decorator import on_save
from noc.core.defer import call_later

import cachetools


@on_save
class ServiceProfile(Document):
    meta = {
        "collection": "noc.serviceprofiles"
    }
    name = StringField(unique=True)
    description = StringField()
    # Jinja2 service label template
    card_title_template = StringField()
    # FontAwesome glyph
    glyph = StringField()
    # Auto-assign interface profile when service binds to interface
    interface_profile = ReferenceField(InterfaceProfile)
    # Alarm weight
    weight = IntField(default=0)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"))
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
    from service import Service
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
