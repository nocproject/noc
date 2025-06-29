# ----------------------------------------------------------------------
# MessageRoute
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Optional, Union
import threading
import operator

# Third-party modules
import bson
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    ListField,
    EmbeddedDocumentListField,
    EnumField,
)
from mongoengine.errors import ValidationError

# NOC modules
from noc.core.mx import MessageType, MESSAGE_HEADERS, MessageMeta
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField, PlainReferenceListField
from noc.core.change.decorator import change
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.resourcegroup import ResourceGroup
from noc.config import config
from .handler import Handler
from .template import Template
from .notificationgroup import NotificationGroup
from .label import Label

id_lock = threading.Lock()


class HeaderMatch(EmbeddedDocument):
    header = StringField(choices=list(sorted(MESSAGE_HEADERS)))
    op = StringField(choices=["==", "!=", "regex"])
    value = StringField()

    def __str__(self):
        return "%s %s %s" % (self.op, self.header, self.value)

    @property
    def is_eq(self) -> bool:
        return self.op == "=="

    @property
    def is_ne(self) -> bool:
        return self.op == "!="

    @property
    def is_re(self) -> bool:
        return self.op == "regex"


class MRMatch(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    resource_groups = PlainReferenceListField(ResourceGroup)
    administrative_domain = ForeignKeyField(AdministrativeDomain)
    headers_match = EmbeddedDocumentListField(HeaderMatch)

    def __str__(self):
        return f'{", ".join(self.labels)}, {self.administrative_domain or ""}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


class MRAHeader(EmbeddedDocument):
    header = StringField(choices=list(sorted(MESSAGE_HEADERS)))
    value = StringField(required=False)
    transparent = BooleanField(default=False)  # For set - headers translate to Consumer

    def __str__(self):
        return self.header


@change
class MessageRoute(Document):
    meta = {"collection": "messageroutes", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    order = IntField(default=0)
    # Message-Type header value
    type: MessageType = EnumField(MessageType, required=True)
    # Match message headers
    match: List[MRMatch] = EmbeddedDocumentListField(MRMatch)
    #
    telemetry_sample = IntField()
    # Message transmuting handler
    transmute_handler = PlainReferenceField(Handler)
    transmute_template = ForeignKeyField(Template)
    # Message actions
    action = StringField(choices=["drop", "dump", "stream", "notification"], default="notification")
    stream = StringField()
    notification_group = ForeignKeyField(NotificationGroup)
    render_template = ForeignKeyField(Template)
    headers = EmbeddedDocumentListField(MRAHeader)

    _id_cache = cachetools.TTLCache(100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["MessageRoute"]:
        return MessageRoute.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgmxroute:
            yield "cfgmxroute", self.id

    def __str__(self):
        return self.name

    def clean(self):
        if self.type == "metrics" and self.action == "notification":
            raise ValidationError({"action": "For type 'metric' Notification is not allowed"})
        if self.action == "stream" and not self.stream:
            raise ValidationError({"stream": "For 'stream' action Stream must be set"})
        elif self.action == "notification" and not self.notification_group:
            raise ValidationError(
                {"notification_group": "For 'notification' action NotificationGroup must be set"}
            )
        super().clean()

    def get_route_config(self):
        """Return data for configured Router"""
        r = {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "order": self.order,
            "action": self.action,
            "telemetry_sample": self.telemetry_sample,
            "match": [],
        }
        if self.stream:
            r["stream"] = self.stream
        if self.type == "metrics" and self.action == "stream":
            r["action"] = "metrics"
        if self.action == "notification":
            r["action"] = "message"
        if self.headers:
            r["headers"] = [{"header": m.header, "value": m.value} for m in self.headers]
        if self.notification_group:
            r["notification_group"] = str(self.notification_group.id)
        if self.render_template:
            r["render_template"] = str(self.render_template.id)
        if self.transmute_template:
            r["transmute_template"] = str(self.transmute_template.id)
        if self.transmute_handler:
            r["transmute_handler"] = str(self.transmute_handler.id)
        for match in self.match:
            r["match"] += [
                {
                    MessageMeta.LABELS.value: list(match.labels),
                    "exclude_labels": list(match.exclude_labels),
                    MessageMeta.ADM_DOMAIN.value: (
                        AdministrativeDomain.get_nested_ids(match.administrative_domain)
                        if match.administrative_domain
                        else None
                    ),
                    MessageMeta.GROUPS.value: [str(g.id) for g in match.resource_groups or []],
                    "headers": [
                        {"header": m.header, "op": m.op, "value": m.value}
                        for m in match.headers_match or []
                    ],
                }
            ]
        return r
