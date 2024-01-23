# ----------------------------------------------------------------------
# ObjectValidationPolicy
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
from typing import Iterable, Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    EmbeddedDocumentField,
    DictField,
)
from jinja2 import Template
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.fm.models.alarmclass import AlarmClass
from noc.core.models.problem import ProblemItem
from .confdbquery import ConfDBQuery

id_lock = threading.Lock()


class ObjectValidationRule(EmbeddedDocument):
    query = PlainReferenceField(ConfDBQuery)
    query_params = DictField()
    filter_query = PlainReferenceField(ConfDBQuery)
    is_active = BooleanField(default=True)
    error_code = StringField()
    error_text_template = StringField(default="{{error}}")
    alarm_class = PlainReferenceField(AlarmClass)
    is_fatal = BooleanField(default=False)

    def __str__(self):
        return self.query.name


@on_delete_check(check=[("sa.ManagedObjectProfile", "object_validation_policy")])
class ObjectValidationPolicy(Document):
    meta = {"collection": "objectvalidationpolicies", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    filter_query = PlainReferenceField(ConfDBQuery)
    rules = ListField(EmbeddedDocumentField(ObjectValidationRule))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ObjectValidationPolicy"]:
        return ObjectValidationPolicy.objects.filter(id=oid).first()

    def iter_problems(self, engine) -> Iterable[ProblemItem]:
        """
        Check rules against ConfDB engine

        :param engine: ConfDB Engine instance
        :return: List of problems
        """
        # Check filter query, if any
        if self.filter_query:
            if not self.filter_query.any(engine):
                return
        # Process rules
        for rule in self.rules:
            if not rule.is_active:
                continue
            if rule.filter_query:
                if not rule.filter_query.any(engine):
                    continue
            for ctx in rule.query.query(engine, **rule.query_params):
                if "error" in ctx:
                    tpl = Template(rule.error_text_template)
                    path = []
                    if rule.error_code:
                        path += [rule.error_code]
                    yield ProblemItem(
                        alarm_class=rule.alarm_class.name if rule.alarm_class else None,
                        path=path,
                        message=tpl.render(ctx),
                        code=rule.error_code or None,
                    )
                    if rule.is_fatal:
                        return
