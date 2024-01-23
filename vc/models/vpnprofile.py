# ----------------------------------------------------------------------
# VPN Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.main.models.template import Template
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@Label.model
@bi_sync
@on_delete_check(
    check=[
        ("vc.VPN", "profile"),
        ("ip.VRF", "profile"),
        ("sa.ManagedObjectProfile", "vpn_profile_interface"),
        ("sa.ManagedObjectProfile", "vpn_profile_mpls"),
        ("sa.ManagedObjectProfile", "vpn_profile_confdb"),
    ]
)
class VPNProfile(Document):
    meta = {"collection": "vpnprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    type = StringField(
        choices=[
            ("vrf", "VRF"),
            ("vxlan", "VxLAN"),
            ("vpls", "VPLS"),
            ("vll", "VLL"),
            ("evpn", "EVPN"),
            ("ipsec", "IPSec"),
            ("gre", "GRE"),
            ("ipip", "IP-IP"),
        ],
        default="vrf",
    )
    workflow = PlainReferenceField(Workflow)
    # Template.subject to render VPN/VRF.name
    name_template = ForeignKeyField(Template)
    #
    style = ForeignKeyField(Style)
    # For vrf type -- default prefix profile
    # Used to create AFI root prefixes
    default_prefix_profile = PlainReferenceField("ip.PrefixProfile")
    # Labels
    labels = ListField(StringField())
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
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["VPNProfile"]:
        return VPNProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["VPNProfile"]:
        return VPNProfile.objects.filter(bi_id=bi_id).first()

    def clean(self):
        if self.type == "vrf" and not self.default_prefix_profile:
            raise ValidationError("default_prefix_profile must be set for vrf type")

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_vpn")
