# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Network Segment Profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
import cachetools
from threading import Lock

# Third-party modules
import six
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    ListField,
    EmbeddedDocumentField,
    LongField,
)

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.main.models.style import Style
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem

id_lock = Lock()
DEFAULT_UPLINK_POLICY = "seghier"


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
            ("rep", "REP"),
            ("stp", "STP"),
            ("udld", "UDLD"),
            ("fdp", "FDP"),
            ("bfd", "BFD"),
            ("mac", "MAC"),
            ("xmac", "xMAC"),
            ("nri", "NRI"),
        ]
    )
    # Custom method name for *custom*
    # or handler for *handler*
    handler = StringField()
    is_active = BooleanField(default=True)


class UplinkPolicySettings(EmbeddedDocument):
    method = StringField(
        choices=[
            ("seghier", "Segment Hierarchy"),
            ("molevel", "Object Level"),
            ("seg", "All Segment Objects"),
            ("minaddr", "Lesser Management Address"),
            ("maxaddr", "Greater Management Address"),
        ]
    )
    is_active = BooleanField(default=True)


@bi_sync
@on_delete_check(
    check=[("inv.NetworkSegment", "profile"), ("inv.NetworkSegmentProfile", "autocreated_profile")]
)
@on_save
@six.python_2_unicode_compatible
class NetworkSegmentProfile(Document):
    meta = {"collection": "noc.networksegmentprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField(required=False)
    # segment discovery interval
    discovery_interval = IntField(default=86400)
    # Segment style
    style = ForeignKeyField(Style, required=False)
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
        choices=[("E", "Always Enable"), ("C", "Calculate"), ("D", "Disable")], default="D"
    )
    # Default profile for autocreated children segments
    # (i.e. during autosegmentation)
    # Copy this segment profile otherwise
    autocreated_profile = PlainReferenceField("self")
    # List of enabled topology method
    # in order of preference (most preferable first)
    topology_methods = ListField(EmbeddedDocumentField(SegmentTopologySettings))
    # List of uplink policies (most preferable first)
    uplink_policy = ListField(EmbeddedDocumentField(UplinkPolicySettings))
    # Enable VLAN discovery for appropriative management objects
    enable_vlan = BooleanField(default=False)
    # Default VLAN profile for discovered VLANs
    default_vlan_profile = PlainReferenceField("vc.VLANProfile")
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return NetworkSegmentProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return NetworkSegmentProfile.objects.filter(bi_id=id).first()

    def on_save(self):
        if hasattr(self, "_changed_fields") and "discovery_interval" in self._changed_fields:
            from .networksegment import NetworkSegment

            for ns in NetworkSegment.objects.filter(profile=self.id):
                ns.ensure_discovery_jobs()

    def get_topology_methods(self):
        ml = getattr(self, "_topology_methods", None)
        if not ml:
            ml = [
                m.method
                for m in self.topology_methods
                if m.is_active and m not in ("custom", "handler")
            ]
            self._topology_methods = ml
        return ml

    def is_preferable_method(self, m1, m2):
        """
        Returns True if m1 topology discovery method is
        preferable over m2
        """
        if not m2:
            # Always override unknown method
            return True
        if m1 == m2:
            # Method can refine itself
            return True
        try:
            methods = self.get_topology_methods()
            i1 = methods.index(m1)
            i2 = methods.index(m2)
        except ValueError:
            return False
        return i1 <= i2

    def iter_uplink_policy(self):
        """
        Yields all enabled uplinks policies in order of preference
        :return:
        """
        n = 0
        for p in self.uplink_policy:
            if p.is_active:
                yield p.method
                n += 1
        if not n:
            yield DEFAULT_UPLINK_POLICY
