# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Supplier Group
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, LongField
import cachetools
# NOC modules
from noc.lib.nosql import ForeignKeyField, PlainReferenceField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.style import Style
from noc.wf.models.workflow import Workflow
from noc.core.bi.decorator import bi_sync

id_lock = Lock()


@bi_sync
class SupplierProfile(Document):
    meta = {
        "collection": "noc.supplierprofiles",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    description = StringField()
    workflow = PlainReferenceField(Workflow)
    style = ForeignKeyField(Style, required=False)
    tags = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return SupplierProfile.objects.filter(id=id).first()
