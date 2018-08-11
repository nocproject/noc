# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ResourceGroup model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
import threading
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField
import cachetools
# NOC modules
from noc.lib.nosql import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from .technology import Technology

id_lock = threading.Lock()


@bi_sync
@on_delete_check(check=[
    ("inv.ResourceGroup", "parent"),
    # sa.ManagedObject
    ("sa.ManagedObject", "static_service_groups"),
    ("sa.ManagedObject", "effective_service_groups"),
    ("sa.ManagedObject", "static_client_groups"),
    ("sa.ManagedObject", "effective_client_groups"),
    # sa.ManagedObjectSelector
    ("sa.ManagedObjectSelector", "filter_service_group"),
    ("sa.ManagedObjectSelector", "filter_client_group"),
])
class ResourceGroup(Document):
    """
    Technology

    Abstraction to restrict ResourceGroup links
    """
    meta = {
        "collection": "resourcegroups",
        "strict": False,
        "auto_create_index": False
    }

    # Group | Name
    name = StringField()
    technology = PlainReferenceField(Technology)
    parent = PlainReferenceField("inv.ResourceGroup")
    description = StringField()
    # @todo: FM integration
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Tags
    tags = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.technology.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ResourceGroup.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return ResourceGroup.objects.filter(bi_id=id).first()
