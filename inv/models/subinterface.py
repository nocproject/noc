## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SubInterface model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import (Document, PlainReferenceField,
                           ForeignKeyField, StringField, BooleanField,
                           ListField, IntField)
from forwardinginstance import ForwardingInstance
from interface import Interface
from noc.sa.models import ManagedObject
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.project.models.project import Project


SUBINTERFACE_AFI = (
    IGetInterfaces.returns
    .element.attrs["interfaces"]
    .element.attrs["subinterfaces"]
    .element.attrs["enabled_afi"].element.choices)

SUBINTERFACE_PROTOCOLS = (
    IGetInterfaces.returns
    .element.attrs["interfaces"]
    .element.attrs["subinterfaces"]
    .element.attrs["enabled_protocols"].element.choices)

TUNNEL_TYPES = (
    IGetInterfaces.returns
    .element.attrs["interfaces"]
    .element.attrs["subinterfaces"]
    .element.attrs["tunnel"]
    .attrs["type"].choices
)


class SubInterface(Document):
    meta = {
        "collection": "noc.subinterfaces",
        "allow_inheritance": False,
        "indexes": [
            ("managed_object", "ifindex"),
            ("managed_object", "vlan_ids"),
            "interface", "managed_object",
            "untagged_vlan", "tagged_vlans",
            "enabled_afi"
        ]
    }
    interface = PlainReferenceField(Interface)
    managed_object = ForeignKeyField(ManagedObject)
    forwarding_instance = PlainReferenceField(
        ForwardingInstance, required=False)
    name = StringField()
    description = StringField(required=False)
    mtu = IntField(required=False)
    mac = StringField(required=False)
    vlan_ids = ListField(IntField(), default=[])
    enabled_afi = ListField(StringField(
        choices=[(x, x) for x in SUBINTERFACE_AFI]
    ), default=[])
    ipv4_addresses = ListField(StringField(), default=[])
    ipv6_addresses = ListField(StringField(), default=[])
    iso_addresses = ListField(StringField(), default=[])
    vpi = IntField(required=False)
    vci = IntField(required=False)
    enabled_protocols = ListField(StringField(
        choices=[(x, x) for x in SUBINTERFACE_PROTOCOLS]
    ), default=[])
    untagged_vlan = IntField(required=False)
    tagged_vlans = ListField(IntField(), default=[])
    # ip_unnumbered_subinterface
    ifindex = IntField(required=False)
    # Tunnel services
    tunnel_type = StringField(
        choices=[(x, x) for x in TUNNEL_TYPES], required=False)
    tunnel_local_address = StringField(required=False)
    tunnel_remote_address = StringField(required=False)
    project = ForeignKeyField(Project)

    def __unicode__(self):
        return "%s %s" % (self.interface.managed_object.name, self.name)
