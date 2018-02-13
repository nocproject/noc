# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Workflow model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock
import operator
import logging
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField,
                                ReferenceField, LongField)
import cachetools
# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem

logger = logging.getLogger(__name__)
id_lock = Lock()


@bi_sync
@on_delete_check(check=[
    ("wf.State", "workflow"),
    ("ip.AddressProfile", "workflow"),
    ("ip.PrefixProfile", "workflow"),
    ("crm.SubscriberProfile", "workflow"),
    ("crm.SupplierProfile", "workflow")
])
class Workflow(Document):
    meta = {
        "collection": "workflows",
        "strict": False,
        "auto_create_index": False
    }
    name = StringField(unique=True)
    is_active = BooleanField()
    description = StringField()
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _default_state_cache = cachetools.TTLCache(maxsize=1000, ttl=1)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Workflow.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return Workflow.objects.filter(bi_id=id).first()

    @cachetools.cachedmethod(operator.attrgetter("_default_state_cache"), lock=lambda _: id_lock)
    def get_default_state(self):
        from .state import State
        return State.objects.filter(workflow=self.id, is_default=True).first()

    def set_default_state(self, state):
        from .state import State
        logger.info("[%s] Set default state to: %s",
                    self.name, state.name)
        for s in State.objects.filter(workflow=self.id):
            if s.is_default and s.id != state.id:
                logger.info("[%s] Removing default status from: %s",
                            self.name, s.name)
                s.is_default = False
                s.save()
