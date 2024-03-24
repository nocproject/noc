# ----------------------------------------------------------------------
# State transition
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import operator
import logging
from typing import List, Dict, Any, Optional, Union
from threading import Lock

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ReferenceField,
    LongField,
    ListField,
    BooleanField,
    IntField,
    EmbeddedDocumentField,
    UUIDField,
)
import cachetools

# NOC modules
from .workflow import Workflow
from .state import State
from noc.core.mongo.fields import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.main.models.remotesystem import RemoteSystem
from noc.core.handler import get_handler

from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json

logger = logging.getLogger(__name__)
id_lock = Lock()


class RequiredRule(EmbeddedDocument):
    labels: List[str] = ListField(StringField())
    exclude_labels: List[str] = ListField(StringField())

    def __str__(self):
        return f'{", ".join(self.labels)}'

    def json_data(self) -> Dict[str, Any]:
        r = {
            "labels": [h for h in self.labels],
            "exclude_labels": [e for e in self.exclude_labels],
        }
        return r

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

    def json_data(self) -> Dict[str, Any]:
        r = {
            "x": self.x,
            "y": self.y,
        }
        return r

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


@bi_sync
class Transition(Document):
    meta = {
        "collection": "transitions",
        "indexes": [
            {"fields": ["workflow", "from_state", "to_state", "label"], "unique": True},
            "to_state",
            "required_rules.labels",
        ],
        "strict": False,
        "auto_create_index": False,
        "json_collection": "wf.transitions",
        "json_depends_on": ["wf.workflows", "wf.states"],
        "json_unique_fields": [("workflow", "from_state", "to_state", "label")],
    }
    workflow: Workflow = PlainReferenceField(Workflow)
    from_state: State = PlainReferenceField(State)
    to_state: State = PlainReferenceField(State)
    uuid = UUIDField(binary=True)
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
    _active_transition_cache = cachetools.TTLCache(maxsize=100, ttl=600)

    def __str__(self):
        return "%s[%s]: %s -> %s" % (
            self.workflow.name,
            self.label,
            str(self.from_state.name),
            str(self.to_state.name),
        )

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "workflow__name": self.workflow.name,
            "from_state__uuid": str(self.from_state.uuid),
            "to_state__uuid": str(self.to_state.uuid),
            "uuid": self.uuid,
            "is_active": self.is_active,
            "$collection": self._meta["json_collection"],
            "label": self.label,
            "enable_manual": self.enable_manual,
        }
        if self.description:
            r["description"] = self.description
        if self.event:
            r["event"] = self.event
        if self.handlers:
            r["handlers"] = [h for h in self.handlers]
        if self.required_rules:
            r["required_rules"] = [r.json_data() for r in self.required_rules]
        if self.vertices:
            r["vertices"] = [r.json_data() for r in self.vertices]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "workflow__name",
                "from_state__uuid",
                "to_state__uuid",
                "uuid",
                "is_active",
                "$collection",
                "event",
                "label",
                "description",
                "enable_manual",
                "handlers",
                "required_rules",
                "vertices",
            ],
        )

    def get_json_path(self) -> str:
        name_coll = quote_safe_path(
            " ".join([self.workflow.name, self.from_state.name, self.to_state.name, self.label])
        )
        return os.path.join(name_coll) + ".json"

    @property
    def json_name(self):
        return str(self)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Transition"]:
        return Transition.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Transition"]:
        return Transition.objects.filter(bi_id=bi_id).first()

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

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_active_transition_cache"), lock=lambda _: id_lock
    )
    def get_active_transitions(cls, state: str, event: str) -> List["Transition"]:
        return list(Transition.objects.filter(from_state=state, event=event, is_active=True))
