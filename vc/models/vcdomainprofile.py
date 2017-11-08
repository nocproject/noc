# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VCDomainProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock
import operator
from collections import namedtuple
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, LongField
import cachetools
# NOC modules
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
from noc.lib.nosql import PlainReferenceField, ForeignKeyField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.wf.models.workflow import Workflow
from .vcfilter import VCFilter

id_lock = Lock()

VCTypeDescription = namedtuple(
    "VCTypeDescription",
    ["type", "name",
     # Minimal amount of labels
     "min_labels",
     # L1 range
     "l1_min", "l1_max",
     # L2 range (0 if not used)
     "l2_min", "l2_max"])

VC_TYPE_DESCRIPTIONS = [
    # type, name, min_labels, l1_min, l1_max, l2_min, l2_max
    VCTypeDescription("q", "802.1Q VLAN", 1, 1, 4095, 0, 0),
    VCTypeDescription("Q", "802.1ad Q-in-Q", 2, 1, 4095, 1, 4095),
    VCTypeDescription("D", "FR DLCI", 1, 16, 991, 0, 0),
    VCTypeDescription("M", "MPLS", 1, 16, 1048575, 16, 1048575),
    VCTypeDescription("A", "ATM VCI/VPI", 1, 0, 65535, 0, 4095),
    VCTypeDescription("X", "X.25 group/channel", 2, 0, 15, 0, 255),
]

VC_TYPES = dict((t.type, t.name) for t in VC_TYPE_DESCRIPTIONS)


@bi_sync
@on_delete_check(check=[
    ("vc.VCDomain", "profile")
])
class VCDomainProfile(Document):
    meta = {
        "collection": "vcdomainprofiles",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    description = StringField()
    #
    type = StringField(
        choices=[(t.type, t.name) for t in VC_TYPE_DESCRIPTIONS],
        default=VC_TYPE_DESCRIPTIONS[0].type
    )
    # Permit VLAN discovery
    enable_vlan_discovery = BooleanField(default=False)
    # Style
    style = ForeignKeyField(Style)
    # Default workflows for new VC
    default_vc_workflow = PlainReferenceField(Workflow)
    # Permit VLAN provisioning
    enable_vlan_provisioning = BooleanField(default=False)
    # Filter VLANs for provisioning
    vlan_provisioning_filter = ForeignKeyField(VCFilter)
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return VCDomainProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return VCDomainProfile.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"),
                             lock=lambda _: id_lock)
    def get_default_profile(cls):
        return VCDomainProfile.objects.filter(
            name=cls.DEFAULT_PROFILE_NAME).first()

    @property
    def type_description(self):
        return VC_TYPES[self.type]
