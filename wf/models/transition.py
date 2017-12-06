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
import logging
from exceptions import ImportError
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, ReferenceField, LongField,
                                ListField, BooleanField)
import cachetools
# NOC modules
from .workflow import Workflow
from .state import State
from noc.lib.nosql import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.core.handler import get_handler

logger = logging.getLogger(__name__)
id_lock = Lock()


@bi_sync
class Transition(Document):
    meta = {
        "collection": "transitions",
        "indexes": [
            "from_state",
            "to_state"
        ],
        "strict": False,
        "auto_create_index": False
    }
    workflow = PlainReferenceField(Workflow)
    from_state = PlainReferenceField(State)
    to_state = PlainReferenceField(State)
    is_active = BooleanField(default=True)
    # Event name
    # Some predefined names exists:
    # seen -- discovery confirms resource usage
    # expired - TTL expired
    event = StringField()
    # Text label
    label = StringField()
    # Arbbitrary description
    description = StringField()
    # Enable manual transition
    enable_manual = BooleanField(default=True)
    # Handler to be called on starting transitions
    # Any exception aborts transtion
    handlers = ListField(StringField())
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

    def clean(self):
        if not self.from_state or not self.to_state:
            raise ValueError("Missed state")
        if self.from_state.workflow != self.to_state.workflow:
            raise ValueError("Workflow mismatch")
        self.workflow = self.from_state.workflow

    def on_transition(self, obj):
        """
        Called during transition
        :param obj:
        :return:
        """
        if self.handlers:
            logger.debug("[%s|%s|%s] Running transition handlers",
                         obj, obj.state.name, self.label)
            for hn in self.handlers:
                try:
                    h = get_handler(str(hn))
                except ImportError as e:
                    logger.error("Error import handler: %s" % e)
                    h = None
                if h:
                    logger.debug("[%s|%s|%s] Running %s",
                                 obj, obj.state.name,
                                 self.label, hn)
                    h(obj)  # @todo: Catch exceptions
                else:
                    logger.debug("[%s|%s|%s] Invalid handler %s, skipping",
                                 obj, obj.state.name,
                                 self.label, hn)
