# ----------------------------------------------------------------------
# CapsProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import operator
from typing import Optional, Union, List

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    DynamicField,
    ReferenceField,
    EmbeddedDocumentListField,
)
import cachetools

# NOC modules
from noc.core.caps.types import CapsConfig
from noc.core.model.decorator import on_delete_check
from noc.core.change.decorator import change
from noc.inv.models.capability import Capability
from noc.main.models.label import Label

id_lock = threading.Lock()


class CapsSettings(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    # Required
    capability: Capability = ReferenceField(Capability, required=True)
    default_value = DynamicField()
    allow_manual = BooleanField(default=False)
    # Add to Reference
    ref_scope = StringField(required=False)
    # Wildcard
    set_label: Optional["Label"] = ReferenceField(Label, required=False)
    # ref_remote_system

    def __str__(self):
        return f"{self.capability.name}: D:{self.default_value}; M: {self.allow_manual}"

    def clean(self):
        super().clean()
        if self.default_value:
            self.capability.clean_value(self.default_value)
        if self.set_label:
            if not self.set_label.is_wildcard and not self.capability.type.is_logical:
                raise ValueError("Only wildcard label may by set")
            if self.capability.type.is_logical and self.set_label.is_scoped:
                raise ValueError("On boolean type only not-scoped Set")

    def get_config(self) -> CapsConfig:
        """"""
        return CapsConfig(
            default_value=self.default_value or None,
            allow_manual=self.allow_manual,
            ref_scope=self.ref_scope,
            set_label=self.set_label.name if self.set_label else None,
        )


@change
@on_delete_check(
    check=[("sa.ManagedObjectProfile", "caps_profile"), ("sa.ServiceProfile", "caps_profile")]
)
class CapsProfile(Document):
    meta = {"collection": "capsprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    # Enable snmp protocol discovery
    enable_snmp = BooleanField(default=True)
    enable_snmp_v1 = BooleanField(default=True)
    enable_snmp_v2c = BooleanField(default=True)
    # Enable L2 protocols caps discovery
    enable_l2 = BooleanField(default=False)
    bfd_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    cdp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    fdp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    huawei_ndp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    lacp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    lldp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    oam_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    rep_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    stp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    udld_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    # Enable L3 protocols caps discovery
    enable_l3 = BooleanField(default=False)
    hsrp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    vrrp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    vrrpv3_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    bgp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    ospf_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    ospfv3_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    isis_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    ldp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    rsvp_policy = StringField(
        choices=[
            ("D", "Disable"),  # Always disable
            ("T", "Enable for Topology"),  # Enable if appropriate topology discovery is enabled
            ("E", "Enable"),  # Always enable
        ],
        default="T",
    )
    # Capabilities
    caps: List[CapsSettings] = EmbeddedDocumentListField(CapsSettings)

    L2_SECTIONS = ["bfd", "cdp", "fdp", "huawei_ndp", "lacp", "lldp", "oam", "rep", "stp", "udld"]
    L3_SECTIONS = ["hsrp", "vrrp", "vrrpv3", "bgp", "ospf", "ospfv3", "isis", "ldp", "rsvp"]

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["CapsProfile"]:
        return CapsProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls):
        return CapsProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()

    def get_sections(self, mop, nsp) -> List[str]:
        """
        Returns a list of enabled sections
        Args:
            mop: Managed Object Profile instance
            nsp: Network Segment Profile instance
        """

        def l2_is_enabled(method):
            cp = getattr(self, "%s_policy" % method)
            if cp == "E":
                return True
            if cp == "D":
                return False
            mopp = getattr(mop, "enable_box_discovery_%s" % method)
            if not mopp:
                return False
            tm = nsp.get_topology_methods()
            return method in tm

        def l3_is_enabled(method):
            cp = getattr(self, "%s_policy" % method)
            # Treat `T` policy as `E` temporarily
            return cp != "D"

        r = []
        if self.enable_snmp:
            r += ["snmp"]
            if self.enable_snmp_v1:
                r += ["snmp_v1"]
            if self.enable_snmp_v2c:
                r += ["snmp_v2c"]
        if self.enable_l2:
            r += [m for m in self.L2_SECTIONS if l2_is_enabled(m)]
        if self.enable_l3:
            r += [m for m in self.L3_SECTIONS if l3_is_enabled(m)]
        return r
