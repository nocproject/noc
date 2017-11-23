# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# State model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, ListField,
                                ReferenceField, LongField, IntField)
import cachetools
# NOC modules
from .workflow import Workflow
from noc.lib.nosql import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem


id_lock = Lock()


@bi_sync
@on_delete_check(check=[
    ("wf.Transition", "from_state"),
    ("wf.Transition", "to_state"),
])
class State(Document):
    meta = {
        "collection": "states",
        "indexes": [
            {
                "fields": ["workflow", "name"],
                "unique": True
            }
        ],
        "strict": False,
        "auto_create_index": False
    }
    workflow = PlainReferenceField(Workflow)
    name = StringField()
    description = StringField()
    # State properties
    # Default state for workflow (starting state if not set explicitly)
    is_default = BooleanField(default=False)
    # Resource is in productive usage
    is_productive = BooleanField(default=False)
    # Discovery should update last_seen field
    update_last_seen = BooleanField(default=False)
    # State time-to-live in seconds
    # 0 - infinitive TTL
    # >0 - Set *expired* field to now + ttl
    #      Send *expired* signal when TTL expired
    # Expiration may also be delayed by *update_expired* setting
    ttl = IntField(default=0)
    # Update ttl every time when object is discovered
    update_expired = BooleanField(default=False)
    # Handler to be called on entering state
    on_enter_handlers = ListField(StringField())
    # Job to be started when entered state (jcls)
    # Job key will be <state id>-<resource model>-<resource id>
    job_handler = StringField()
    # Handlers to be called on leaving state
    on_leave_handlers = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __unicode__(self):
        return u"%s: %s" % (self.workflow.name, self.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return State.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return State.objects.filter(bi_id=id).first()
