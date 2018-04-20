# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## Workflow model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
import noc.lib.nosql as nosql
from solution import Solution
from error import InvalidStartNode


class Workflow(nosql.Document):
    meta = {
        "collection": "noc.wf.workflows",
        "allow_inheritance": False
    }

    # Unique identifier
    name = nosql.StringField()
    # Long name
    display_name = nosql.StringField()
    solution = nosql.PlainReferenceField(Solution)
    version = nosql.IntField()
    is_active = nosql.BooleanField()
    description = nosql.StringField()
    #
    start_node = nosql.StringField()
    # Permissions
    # stat_permission = nosql.StringField()
    # trace_permission = nosql.StringField()
    # kill_permission = nosql.StringField()
    trace = nosql.BooleanField(default=False)

    def __unicode__(self):
        return "%s.%s v%s" % (
            self.solution.name, self.name, self.version)

    def get_node(self, name):
        return Node.objects.filter(workflow=self.id, name=name).first()

    def get_start_node(self):
        return Node.objects.filter(
            workflow=self.id, id=self.start_node).first()

    def run(self, _trace=None, **kwargs):
        """
        Run process
        :param kwargs:
        :return: Process instance
        """
        # Find start node
        start_node = self.get_start_node()
        if not start_node:
            raise InvalidStartNode(self.start_node)
        #
        trace = self.trace if _trace is None else _trace
        # Prepare context
        ctx = {}
        for v in Variable.objects.filter(workflow=self.id):
            if v.name in kwargs:
                ctx[v.name] = v.clean(kwargs[v.name])
            elif v.default:
                ctx[v.name] = v.clean(v.default)
            else:
                ctx[v.name] = None

        p = Process(
            workflow=self,
            context=ctx,
            start_time=datetime.datetime.now(),
            node=start_node,
            trace=trace
        )
        p.save()
        # Schedule job
        p.schedule()
        return p

## Avoid circular references
from variable import Variable
from process import Process
from node import Node
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
