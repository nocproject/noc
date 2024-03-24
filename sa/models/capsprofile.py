# ----------------------------------------------------------------------
# CapsProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = threading.Lock()


@on_delete_check(check=[("sa.ManagedObjectProfile", "caps_profile")])
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
    #
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

    def get_sections(self, mop, nsp):
        """
        Returns a list of enabled sections
        :param mop: Managed Object Profile instance
        :param nsp: Network Segment Profile instance
        :return: List of string
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
