# ----------------------------------------------------------------------
# MessageRoute
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, BooleanField, IntField, ListField, EmbeddedDocumentField

# NOC modules
from noc.core.mx import MESSAGE_TYPES, MESSAGE_HEADERS
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from .handler import Handler
from .template import Template
from .notificationgroup import NotificationGroup


class MRMatch(EmbeddedDocument):
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


class MRTransmute(EmbeddedDocument):
    type = StringField(choices=["template", "handler"])
    handler = PlainReferenceField(Handler)
    template = ForeignKeyField(Template)

    def __str__(self):
        return self.type


class MRAHeader(EmbeddedDocument):
    header = StringField(choices=list(sorted(MESSAGE_HEADERS)))
    value = StringField()

    def __str__(self):
        return self.header


class MRAction(EmbeddedDocument):
    type = StringField(choices=["drop", "stream", "notification"])
    stream = StringField()
    notification_group = ForeignKeyField(NotificationGroup)
    headers = ListField(EmbeddedDocumentField(MRAHeader))

    def __str__(self):
        return self.type


class MessageRoute(Document):
    meta = {"collection": "messageroutes", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    order = IntField(default=0)
    # Message-Type header value
    type = StringField(choices=list(sorted(MESSAGE_TYPES)))
    # Match message headers
    match = ListField(EmbeddedDocumentField(MRMatch))
    # Message transmuting pipeline
    transmute = ListField(EmbeddedDocumentField(MRTransmute))
    # Message actions
    action = ListField(EmbeddedDocumentField(MRAction))

    def __str__(self):
        return self.name
