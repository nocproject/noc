# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ASProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField
import cachetools
# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.lib.nosql import PlainReferenceField, ForeignKeyField
from noc.main.models.style import Style

id_lock = Lock()


@on_delete_check(check=[
    ("peer.AS", "profile")
])
class ASProfile(Document):
    meta = {
        "collection": "asprofiles",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style, required=False)

    enable_discovery_prefix_whois_route = BooleanField(default=False)
    prefix_profile_whois_route = PlainReferenceField("ip.PrefixProfile")

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ASProfile.objects.filter(id=id).first()
