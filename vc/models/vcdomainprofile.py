# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VCDomainProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
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

id_lock = Lock()


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
    # Permit VLAN discovery
    enable_vlan_discovery = BooleanField(default=False)
    # Style
    style = ForeignKeyField(Style)
    # Workflow
    workflow = PlainReferenceField(Workflow)
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
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return VCDomainProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return VCDomainProfile.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls):
        return VCDomainProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
