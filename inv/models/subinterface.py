# ---------------------------------------------------------------------
# SubInterface model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, List, Union, Dict, Any

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, ListField

# NOC modules
from noc.config import config
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.model.decorator import on_delete
from noc.sa.models.managedobject import ManagedObject
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.project.models.project import Project
from noc.core.change.decorator import change
from noc.vc.models.l2domain import L2Domain
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


@on_delete
@Label.model
@change(audit=False)
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
            {"fields": ["ipv4_addresses"], "sparse": True},
            "labels",
            "effective_labels",
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
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

    def __str__(self):
        return f"{self.managed_object.name} {self.name}"

    @classmethod
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["SubInterface"]:
        return SubInterface.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_managedobject:
            yield "managedobject", self.managed_object.id
        if "ipv4_addresses" in changed_fields or "id" in changed_fields:
            yield "cfgtarget", self.managed_object.id

    def on_delete(self):
        from noc.fm.models.activealarm import ActiveAlarm

        # Clear Alarm
        for aa in ActiveAlarm.objects.filter(
            managed_object=self.managed_object, vars__interface=self.name
        ):
            aa.clear_alarm("Delete Interface")

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
        return Label.get_effective_setting(label, setting="enable_interface")

    @classmethod
    def iter_effective_labels(cls, instance: "SubInterface") -> Iterable[List[str]]:
        if instance.tagged_vlans:
            yield Label.get_effective_vlanfilter_labels(
                "subinterface_tagged_vlans", instance.tagged_vlans
            )
        if instance.untagged_vlan:
            yield Label.get_effective_vlanfilter_labels(
                "subinterface_untagged_vlan", [instance.untagged_vlan]
            )
        if instance.ipv4_addresses:
            yield Label.get_effective_prefixfilter_labels(
                "subinterface_ipv4_addresses", instance.ipv4_addresses
            )

    @property
    def service(self):
        from noc.sa.models.serviceinstance import ServiceInstance

        si = ServiceInstance.objects.filter(resources=self.as_resource()).first()
        if si:
            return si.service
        return

    def as_resource(self, path: Optional[str] = None) -> str:
        """
        Convert instance or connection to the resource reference.

        Args:
            path: Optional connection name

        Returns:
            Resource reference
        """
        # return f"if:{self.interface.id}:{self.id}"
        return f"si:{self.id}"

    def get_matcher_ctx(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "labels": list(self.effective_labels),
        }
