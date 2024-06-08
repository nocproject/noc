# ----------------------------------------------------------------------
# Quiz model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Any, Dict, Optional, Union

# Third-party modules
import bson
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    EmbeddedDocumentField,
    ListField,
    UUIDField,
    IntField,
    DateTimeField,
)
import cachetools

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check

id_lock = Lock()

Q_TYPES = [
    "str",  # Arbitrary string
    "bool",  # Yes/No
    "int",  # Integer value
    "cli",  # CLI command. Several commands possible
    "snmp-get",  # OID for SNMP GET
    "snmp-getnext",  # OID for SNMP GETNEXT
]


class QuizChange(EmbeddedDocument):
    date = DateTimeField()
    changes = StringField()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"date": self.date.isoformat(), "changes": self.changes}


class QuizQuestion(EmbeddedDocument):
    # Unique (within quiz) question name/variable name
    name = StringField()
    # Arbitrary formed question
    question = StringField()
    # Answer type
    type = StringField(choices=Q_TYPES)
    when = StringField(default="True")

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"name": self.name, "question": self.question, "type": self.type, "when": self.when}


@on_delete_check(check=[("dev.Spec", "quiz")])
class Quiz(Document):
    meta = {
        "collection": "quiz",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "dev.quiz",
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
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["Quiz"]:
        return Quiz.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return Quiz.objects.filter(name=name).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": str(self.uuid),
            "description": self.description,
            "revision": self.revision,
            "disclaimer": self.disclaimer,
            "changes": [c.json_data for c in self.changes],
            "questions": [c.json_data for c in self.questions],
        }

    def to_json(self) -> str:
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
                "questions",
            ],
        )

    def get_json_path(self) -> str:
        return "%s.json" % quote_safe_path(self.name)
