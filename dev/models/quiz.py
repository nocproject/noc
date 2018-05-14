# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Quiz model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, EmbeddedDocumentField,
                                ListField, UUIDField, IntField, DateTimeField)
import cachetools
# NOC modules
from noc.lib.prettyjson import to_json
from noc.lib.text import quote_safe_path

id_lock = Lock()


class QuizChange(EmbeddedDocument):
    date = DateTimeField()
    changes = StringField()


class QuizQuestion(EmbeddedDocument):
    # Unique (within quiz) question name/variable name
    name = StringField()
    # Arbitrary formed question
    question = StringField()
    # Answer type
    type = StringField(choices=[
        "str",  # Arbitrary string
        "bool",  # Yes/No
        "int",  # Integer value
        "cli",  # CLI command. Several commands possible
        "snmp-get",  # OID for SNMP GET
        "snmp-getnext"  # OID for SNMP GETNEXT
    ])
    when = StringField(default="True")


class Quiz(Document):
    meta = {
        "collection": "quiz",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "dev.quiz"
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    revision = IntField(default=1)
    changes = ListField(EmbeddedDocumentField(QuizChange))
    # Information text before quiz
    disclaimer = StringField()
    # List of questions
    questions = ListField(EmbeddedDocumentField(QuizQuestion))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Quiz.objects.filter(id=id).first()

    @property
    def json_data(self):
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "revision": self.revision,
            "disclaimer": self.disclaimer,
            "changes": [c.json_data for c in self.changes],
            "questions": [c.json_data for c in self.questions]
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
                "disclaimer",
                "changes",
                "questions"
            ]
        )

    def get_json_path(self):
        return "%s.json" % quote_safe_path(self.name)
