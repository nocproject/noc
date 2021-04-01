# ----------------------------------------------------------------------
# Prefix Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField, BooleanField
import cachetools

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.main.models.template import Template
from noc.main.models.label import Label
from noc.wf.models.workflow import Workflow
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@Label.model
@bi_sync
@on_delete_check(
    check=[
        ("ip.Prefix", "profile"),
        ("sa.ManagedObjectProfile", "prefix_profile_interface"),
        ("sa.ManagedObjectProfile", "prefix_profile_neighbor"),
        ("sa.ManagedObjectProfile", "prefix_profile_confdb"),
        ("vc.VPNProfile", "default_prefix_profile"),
        ("peer.ASProfile", "prefix_profile_whois_route"),
    ]
)
class PrefixProfile(Document):
    meta = {"collection": "prefixprofiles", "strict": False, "auto_create_index": False}

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
    # Prefix workflow
    workflow = PlainReferenceField(Workflow)
    style = ForeignKeyField(Style)
    # Template.subject to render Prefix.name
    name_template = ForeignKeyField(Template)
    # Discovery policies
    prefix_discovery_policy = StringField(choices=[("E", "Enable"), ("D", "Disable")], default="D")
    address_discovery_policy = StringField(choices=[("E", "Enable"), ("D", "Disable")], default="D")
    # Send seen event to parent
    seen_propagation_policy = StringField(
        choices=[("P", "Propagate"), ("E", "Enable"), ("D", "Disable")], default="P"
    )
    # Include/Exclude broadcast & network addresses from prefix
    prefix_special_address_policy = StringField(
        choices=[("I", "Include"), ("X", "Exclude")], default="X"
    )
    # Labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
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
        return PrefixProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return PrefixProfile.objects.filter(bi_id=id).first()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_prefixprofile")
