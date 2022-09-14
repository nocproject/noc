# ----------------------------------------------------------------------
# State transition
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import logging
from typing import List
from threading import Lock

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ReferenceField,
    LongField,
    ListField,
    BooleanField,
    IntField,
    EmbeddedDocumentField,
)
import cachetools

# NOC modules
from .workflow import Workflow
from .state import State
from noc.core.mongo.fields import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.core.handler import get_handler

logger = logging.getLogger(__name__)
id_lock = Lock()


class RequiredRule(EmbeddedDocument):
    labels: List[str] = ListField(StringField())
    exclude_labels: List[str] = ListField(StringField())

    def __str__(self):
        return f'{", ".join(self.labels)}'

    def is_match(self, labels: List[str]):
        if self.exclude_labels and not set(self.exclude_labels) - set(labels):
            return False
        if not set(self.labels) - set(labels):
            return True
        return False


class TransitionVertex(EmbeddedDocument):
    # vertex coordinates
    x = IntField(default=0)
    y = IntField(default=0)

    def __str__(self):
        return "%s, %s" % (self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


@bi_sync
class Transition(Document):
    meta = {
        "collection": "transitions",
        "indexes": ["from_state", "to_state", "required_rules.labels"],
        "strict": False,
        "auto_create_index": False,
    }
    workflow: Workflow = PlainReferenceField(Workflow)
    from_state: State = PlainReferenceField(State)
    to_state: State = PlainReferenceField(State)
    is_active = BooleanField(default=True)
    # Event name
    # Some predefined names exists:
    # seen -- discovery confirms resource usage
    # expired - TTL expired
    event = StringField()
    # Text label
    label = StringField()
    # Arbitrary description
    description = StringField()
    # Enable manual transition
    enable_manual = BooleanField(default=True)
    # Handler to be called on starting transitions
    # Any exception aborts transition
    handlers = ListField(StringField())
    #
    required_rules: RequiredRule = ListField(EmbeddedDocumentField(RequiredRule))
    # Visual vertices
    vertices = ListField(EmbeddedDocumentField(TransitionVertex))
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return "%s: %s -> %s [%s]" % (
            self.workflow.name,
            self.from_state.name,
            self.to_state.name,
            self.label,
        )

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

    def is_allowed(self, labels: List[str]) -> bool:
        """
        Check transition allowed
        :param labels:
        :return:
        """
        if not self.required_rules:
            return True
        for rule in self.required_rules:
            if rule.is_match(labels):
                return True
        return False

    def on_transition(self, obj):
        """
        Called during transition
        :param obj:
        :return:
        """
        if self.handlers:
            logger.debug("[%s|%s|%s] Running transition handlers", obj, obj.state.name, self.label)
            for hn in self.handlers:
                try:
                    h = get_handler(str(hn))
                except ImportError as e:
                    logger.error("Error import handler: %s" % e)
                    h = None
                if h:
                    logger.debug("[%s|%s|%s] Running %s", obj, obj.state.name, self.label, hn)
                    h(obj)  # @todo: Catch exceptions
                else:
                    logger.debug(
                        "[%s|%s|%s] Invalid handler %s, skipping",
                        obj,
                        obj.state.name,
                        self.label,
                        hn,
                    )
