# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Network Segment Profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import cachetools
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, IntField,
                                ListField, EmbeddedDocumentField,
                                LongField)
# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.lib.nosql import PlainReferenceField
from noc.main.models.remotesystem import RemoteSystem

id_lock = Lock()


class SegmentTopologySettings(EmbeddedDocument):
    method = StringField(
        choices=[
            # Set by third-party scripts
            ("custom", "Custom ..."),
            # Call handler
            ("handler", "Handler ..."),
            # Builtin methods
            ("cdp", "CDP"),
            ("huawei_ndp", "Huawei NDP"),
            ("lacp", "LACP"),
            ("lldp", "LLDP"),
            ("oam", "OAM"),
            ("stp", "STP"),
            ("udld", "UDLD"),
            ("mac", "MAC"),
            ("nri", "NRI")
        ]
    )
    # Custom method name for *custom*
    # or handler for *handler*
    handler = StringField()
    is_active = BooleanField(default=True)


@bi_sync
@on_delete_check(check=[
    ("inv.NetworkSegment", "profile")
])
class NetworkSegmentProfile(Document):
    meta = {
        "collection": "noc.networksegmentprofiles",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    description = StringField(required=False)
    #
    mac_discovery_interval = IntField(default=86400)
    # Restrict MAC discovery to management vlan
    mac_restrict_to_management_vlan = BooleanField(default=False)
    # Management vlan, to restrict MAC search for MAC topology discovery
    management_vlan = IntField(required=False, min_value=1, max_value=4095)
    # MVR VLAN
    multicast_vlan = IntField(required=False, min_value=1, max_value=4095)
    # Detect lost redundancy condition
    enable_lost_redundancy = BooleanField(default=False)
    # Horizontal transit policy
    horizontal_transit_policy = StringField(
        choices=[
            ("E", "Always Enable"),
            ("C", "Calculate"),
            ("D", "Disable")
        ], default="D"
    )
    # List of enabled topology method
    # in order of preference (most preferable first)
    topology_methods = ListField(EmbeddedDocumentField(SegmentTopologySettings))
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return NetworkSegmentProfile.objects.filter(id=id).first()
