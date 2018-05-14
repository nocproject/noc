# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Spec model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, EmbeddedDocumentField, DateTimeField,
                                ListField, UUIDField, IntField)
import cachetools
# NOC modules
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path
from noc.lib.nosql import PlainReferenceField
from noc.sa.models.profile import Profile
from .quiz import Quiz, Q_TYPES

id_lock = Lock()


class SpecChange(EmbeddedDocument):
    date = DateTimeField()
    changes = StringField()

    def json_data(self):
        return {
            "date": self.date.isoformat(),
            "changes": self.changes
        }


class SpecAnswer(EmbeddedDocument):
    name = StringField()
    type = StringField(choices=Q_TYPES)
    value = StringField()

    def json_data(self):
        return {
            "name": self.name,
            "type": self.type,
            "value": self.value
        }


class Spec(Document):
    meta = {
        "collection": "specs",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "dev.specs"
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    revision = IntField(default=1)
    quiz = PlainReferenceField(Quiz)
    author = StringField()
    profile = PlainReferenceField(Profile)
    changes = ListField(EmbeddedDocumentField(SpecChange))
    answers = ListField(EmbeddedDocumentField(SpecAnswer))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Spec.objects.filter(id=id).first()

    @property
    def json_data(self):
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "revision": self.revision,
            "quiz__name": self.quiz.name,
            "author": self.author,
            "profile__name": self.profile.name,
            "changes": [c.json_data for c in self.changes],
            "answers": [c.json_data for c in self.answers]
        }

    def to_json(self):
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "revision",
                "quiz__name",
                "author",
                "profile__name",
                "answers"
            ]
        )

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"
