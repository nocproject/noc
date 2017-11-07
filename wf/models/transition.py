# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# State transition
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
from mongoengine.fields import (StringField, ReferenceField, LongField,
                                ListField)
import cachetools
# NOC modules
from .state import State
from noc.lib.nosql import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem


id_lock = Lock()


@bi_sync
class Transition(Document):
    meta = {
        "collection": "transitions",
        "indexes": [
            "to_state",
            {
                "fields": ["from_state", "code"],
                "unique": True
            }
        ],
        "strict": False,
        "auto_create_index": False
    }
    from_state = PlainReferenceField(State)
    to_state = PlainReferenceField(State)
    # Code name
    code = StringField()
    # Text label
    label = StringField()
    # Handler to be called on starting transitions
    on_enter_handlers = ListField(StringField())
    # Job to be started on entering transition
    # Job key will be <transition id>-<resource model>-<resource id>
    job_handler = StringField()
    # Handlers to be called on leaving transitions
    on_leave_handlers = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    def __unicode__(self):
        return u"%s: %s" % (self.workflow.name, self.name)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Transition.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return Transition.objects.filter(bi_id=id).first()
