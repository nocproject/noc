# ----------------------------------------------------------------------
# MessageRoute
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Optional
import threading
import operator

# Third-party modules
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, IntField, ListField, EmbeddedDocumentField
from mongoengine.errors import ValidationError

# NOC modules
from noc.core.mx import MESSAGE_TYPES, MESSAGE_HEADERS
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.change.decorator import change
from noc.sa.models.administrativedomain import AdministrativeDomain
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
    administrative_domain = ForeignKeyField(AdministrativeDomain)
    headers_match = ListField(EmbeddedDocumentField(HeaderMatch))

    def __str__(self):
        return f'{", ".join(self.labels)}, {self.administrative_domain or ""}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


class MRAHeader(EmbeddedDocument):
    header = StringField(choices=list(sorted(MESSAGE_HEADERS)))
    value = StringField(required=True)

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
    type = StringField(choices=list(sorted(MESSAGE_TYPES)))
    # Match message headers
    match: List[MRMatch] = ListField(EmbeddedDocumentField(MRMatch))
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
    headers = ListField(EmbeddedDocumentField(MRAHeader))

    _id_cache = cachetools.TTLCache(100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["MessageRoute"]:
        return MessageRoute.objects.filter(id=id).first()

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
        """
        Return data for configured Router
        :return:
        """
        r = {
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
                    "labels": match.labels,
                    "exclude_labels": match.exclude_labels,
                    "administrative_domain": AdministrativeDomain.get_nested_ids(
                        match.administrative_domain
                    )
                    if match.administrative_domain
                    else None,
                    "headers": [
                        {"header": m.header, "op": m.op, "value": m.value}
                        for m in match.headers_match
                    ],
                }
            ]
        return r
