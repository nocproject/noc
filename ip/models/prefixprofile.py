# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Prefix Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField, BooleanField
import cachetools
# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.wf.models.workflow import Workflow
from noc.lib.nosql import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
from .addressprofile import AddressProfile

id_lock = Lock()


@bi_sync
@on_delete_check(check=[
    ("ip.Prefix", "profile")
])
class PrefixProfile(Document):
    meta = {
        "collection": "prefixprofiles",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    description = StringField()
    # Enable nested Address discovery
    # via ARP cache
    enable_ip_discovery = BooleanField(default=False)
    # Enable nested Addresses discovery
    # via active PING probes
    enable_ip_ping_discovery = BooleanField(default=False)
    # Enable nested prefix prefix discovery
    enable_prefix_discovery = BooleanField(default=False)
    # Default prefix profile for children prefixes
    autocreated_prefix_profile = PlainReferenceField("self")
    # Default address profile for children addresses
    autocreated_address_profile = PlainReferenceField(AddressProfile)
    # Prefix workflow
    workflow = PlainReferenceField(Workflow)
    style = ForeignKeyField(Style)
    tags = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return PrefixProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return PrefixProfile.objects.filter(bi_id=id).first()
