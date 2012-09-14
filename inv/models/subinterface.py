## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SubInterface model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import Document, PlainReferenceField,\
    ForeignKeyField, StringField, BooleanField, ListField, IntField
from forwardinginstance import ForwardingInstance
from interface import Interface
from noc.sa.models import ManagedObject


class SubInterface(Document):
    meta = {
        "collection": "noc.subinterfaces",
        "allow_inheritance": False,
        "indexes": [
            "interface", "managed_object",
            "untagged_vlan", "tagged_vlans",
            "enabled_afi",
            "is_bridge", "is_ipv4", "is_ipv6"
        ]
    }
    interface = PlainReferenceField(Interface)
    managed_object = ForeignKeyField(ManagedObject)
    forwarding_instance = PlainReferenceField(
        ForwardingInstance, required=False)
    name = StringField()
    description = StringField(required=False)
    mac = StringField(required=False)
    vlan_ids = ListField(IntField(), default=[])
    enabled_afi = ListField(StringField(
        choices=[(x, x) for x in "IPv4", "IPv6", "ISO", "MPLS", "BRIDGE"]
    ), default=[])
    is_ipv4 = BooleanField(default=False)
    is_ipv6 = BooleanField(default=False)
    is_mpls = BooleanField(default=False)
    is_bridge = BooleanField(default=False)
    ipv4_addresses = ListField(StringField(), default=[])
    ipv6_addresses = ListField(StringField(), default=[])
    iso_addresses = ListField(StringField(), default=[])
    enabled_protocols = ListField(StringField(
        choices=[(x, x) for x in [
            "ISIS", "OSPF", "RIP", "EIGRP",
            "BGP",
            "LDP", "RSVP"
        ]]
    ), default=[])
    is_isis = BooleanField(default=False)
    is_ospf = BooleanField(default=False)
    is_rsvp = BooleanField(default=False)
    is_ldp = BooleanField(default=False)
    is_rip = BooleanField(default=False)
    is_bgp = BooleanField(default=False)
    is_eigrp = BooleanField(default=False)
    untagged_vlan = IntField(required=False)
    tagged_vlans = ListField(IntField(), default=[])
    # ip_unnumbered_subinterface
    ifindex = IntField(required=False)

    def __unicode__(self):
        return "%s %s" % (self.interface.managed_object.name, self.name)
