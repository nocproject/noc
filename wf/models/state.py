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
import logging
from exceptions import ImportError
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BooleanField, ListField,
                                ReferenceField, LongField, IntField)
import cachetools
# NOC modules
from .workflow import Workflow
from noc.lib.nosql import PlainReferenceField
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.core.handler import get_handler
from noc.core.defer import call_later
from noc.models import get_model_id

logger = logging.getLogger(__name__)
id_lock = Lock()

STATE_JOB = "noc.core.wf.transition.state_job"


@bi_sync
@on_delete_check(check=[
    ("wf.Transition", "from_state"),
    ("wf.Transition", "to_state"),
    ("crm.Subscriber", "state"),
    ("crm.Supplier", "state"),
    ("phone.PhoneNumber", "state"),
    ("phone.PhoneRange", "state")
])
@on_save
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
    # WFEditor coordinates
    x = IntField(default=0)
    y = IntField(default=0)
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

    def on_save(self):
        if ((hasattr(self, "_changed_fields") and "is_default" in self._changed_fields) or
                not hasattr(self, "_changed_field")) and self.is_default:
            # New default
            self.workflow.set_default_state(self)

    def on_enter_state(self, obj):
        """
        Called when object enters state
        :param obj:
        :return:
        """
        # Process on enter handlers
        if self.on_enter_handlers:
            logger.debug("[%s|%s] Running on_enter_handlers",
                         obj, obj.state.name)
            for hn in self.on_enter_handlers:
                try:
                    h = get_handler(str(hn))
                except ImportError as e:
                    logger.error("Error import on_enter handler: %s" % e)
                    h = None
                if h:
                    logger.debug("[%s|%s] Running %s",
                                 obj, self.name, hn)
                    h(obj)  # @todo: Catch exceptions
                else:
                    logger.debug("[%s|%s] Invalid handler %s, skipping",
                                 obj, self.name, hn)
        # Run Job handler when necessary
        if self.job_handler:
            logger.debug("[%s|%s] Running job handler %s",
                         obj.self.name, self.job_handler)
            try:
                h = get_handler(self.job_handler)
            except ImportError as e:
                logger.error("Error import state job handler: %s" % e)
                h = None
            if h:
                call_later(
                    STATE_JOB,
                    handler=self.job_handler,
                    model=get_model_id(obj),
                    object=str(obj.pk)
                )
            else:
                logger.debug("[%s|%s] Invalid job handler %s, skipping",
                             obj, self.name, self.job_handler)

    def on_leave_state(self, obj):
        """
        Called when object leaves state
        :param obj:
        :return:
        """
        if self.on_leave_handlers:
            logger.debug("[%s|%s] Running on_leave_handlers",
                         obj, self.name)
            for hn in self.on_leave_handlers:
                try:
                    h = get_handler(str(hn))
                except ImportError as e:
                    logger.error("Error import on_leave_state handler: %s" % e)
                    h = None
                if h:
                    logger.debug("[%s|%s] Running %s",
                                 obj, self.name, hn)
                    h(obj)  # @todo: Catch exceptions
                else:
                    logger.debug("[%s|%s] Invalid handler %s, skipping",
                                 obj, self.name, hn)

    def fire_transition(self, transition, obj):
        """
        Process transition from state
        :param transition:
        :param obj:
        :return:
        """
        assert obj.state == self
        assert transition.from_state == self
        # Leave state
        self.on_leave_state(obj)
        # Process transition
        transition.on_transition(obj)
        # Set new state
        # Raises on_enter handler
        obj.set_state(transition.to_state)

    def fire_event(self, event, obj):
        """
        Fire transition by event name
        :param event:
        :param obj:
        :return:
        """
        from .transition import Transition

        t = Transition.objects.filter(from_state=self.id,
                                      event=event).first()
        if t:
            self.fire_transition(t, obj)
        else:
            logger.debug("[%s|%s] No event handler for '%s'. Skipping",
                         obj, self.name, event)
