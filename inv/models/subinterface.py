# ---------------------------------------------------------------------
# SubInterface model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, List

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, ListField, ReferenceField

# NOC modules
from noc.config import config
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.prefixtable import PrefixTable
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.project.models.project import Project
from noc.core.change.decorator import change
from noc.sa.models.service import Service
from noc.vc.models.l2domain import L2Domain
from noc.vc.models.vcfilter import VCFilter
from noc.main.models.label import Label
from .forwardinginstance import ForwardingInstance
from .interface import Interface
from .interfaceprofile import InterfaceProfile


SUBINTERFACE_AFI = (
    IGetInterfaces.returns.element.attrs["interfaces"]
    .element.attrs["subinterfaces"]
    .element.attrs["enabled_afi"]
    .element.choices
)

SUBINTERFACE_PROTOCOLS = (
    IGetInterfaces.returns.element.attrs["interfaces"]
    .element.attrs["subinterfaces"]
    .element.attrs["enabled_protocols"]
    .element.choices
)

TUNNEL_TYPES = (
    IGetInterfaces.returns.element.attrs["interfaces"]
    .element.attrs["subinterfaces"]
    .element.attrs["tunnel"]
    .attrs["type"]
    .choices
)


@Label.model
@change
class SubInterface(Document):
    meta = {
        "collection": "noc.subinterfaces",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            ("managed_object", "ifindex"),
            ("managed_object", "vlan_ids"),
            "interface",
            "managed_object",
            "untagged_vlan",
            "tagged_vlans",
            "enabled_afi",
            "forwarding_instance",
            "service",
            {"fields": ["ipv4_addresses"], "sparse": True},
        ],
    }
    interface = PlainReferenceField(Interface)
    managed_object = ForeignKeyField(ManagedObject)
    forwarding_instance = PlainReferenceField(ForwardingInstance, required=False)
    l2_domain = PlainReferenceField(L2Domain, required=False)
    name = StringField()
    description = StringField(required=False)
    profile = PlainReferenceField(InterfaceProfile, default=InterfaceProfile.get_default_profile)
    mtu = IntField(required=False)
    mac = StringField(required=False)
    vlan_ids = ListField(IntField(), default=[])
    enabled_afi = ListField(StringField(choices=[(x, x) for x in SUBINTERFACE_AFI]), default=[])
    ipv4_addresses = ListField(StringField(), default=[])
    ipv6_addresses = ListField(StringField(), default=[])
    iso_addresses = ListField(StringField(), default=[])
    vpi = IntField(required=False)
    vci = IntField(required=False)
    enabled_protocols = ListField(
        StringField(choices=[(x, x) for x in SUBINTERFACE_PROTOCOLS]), default=[]
    )
    untagged_vlan = IntField(required=False)
    tagged_vlans = ListField(IntField(), default=[])
    # ip_unnumbered_subinterface
    ifindex = IntField(required=False)
    # Tunnel services
    tunnel_type = StringField(choices=[(x, x) for x in TUNNEL_TYPES], required=False)
    tunnel_local_address = StringField(required=False)
    tunnel_remote_address = StringField(required=False)
    project = ForeignKeyField(Project)
    #
    service = ReferenceField(Service)
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

    def __str__(self):
        return "%s %s" % (self.interface.managed_object.name, self.name)

    @classmethod
    def get_by_id(cls, id) -> Optional["SubInterface"]:
        return SubInterface.objects.filter(id=id).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_managedobject:
            yield "managedobject", self.managed_object.id
        if config.datastream.enable_cfgsyslog and (
            "ipv4_addresses" in changed_fields or "id" in changed_fields
        ):
            yield "cfgsyslog", self.managed_object.id
        if config.datastream.enable_cfgtrap and (
            "ipv4_addresses" in changed_fields or "id" in changed_fields
        ):
            yield "cfgtrap", self.managed_object.id

    @property
    def effective_vc_domain(self):
        return self.interface.effective_vc_domain

    @property
    def effective_vlan_domain(self):
        if self.l2_domain:
            return self.l2_domain
        return self.managed_object.l2_domain

    def get_profile(self):
        if self.profile:
            return self.profile
        else:
            return self.interface.profile

    @classmethod
    def can_set_label(cls, label):
        return False

    @classmethod
    def iter_effective_labels(cls, instance: "Interface") -> Iterable[List[str]]:
        if instance.tagged_vlans:
            lazy_tagged_vlans_labels = list(
                VCFilter.iter_lazy_labels(instance.tagged_vlans, "tagged")
            )
            yield Label.ensure_labels(lazy_tagged_vlans_labels, enable_interface=True)
        if instance.untagged_vlan:
            lazy_untagged_vlans_labels = list(
                VCFilter.iter_lazy_labels([instance.untagged_vlan], "untagged")
            )
            yield Label.ensure_labels(lazy_untagged_vlans_labels, enable_interface=True)
        if instance.ipv4_addresses:
            yield list(PrefixTable.iter_lazy_labels(instance.ipv4_addresses))
