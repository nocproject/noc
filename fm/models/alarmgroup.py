# ---------------------------------------------------------------------
# AlarmGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    LongField,
    ReferenceField,
    EmbeddedDocumentField,
)
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.label import Label
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.core.bi.decorator import bi_sync
from .alarmclass import AlarmClass


id_lock = Lock()


class MatchRule(EmbeddedDocument):
    labels = ListField(StringField())
    alarm_class = ReferenceField(AlarmClass)

    def __str__(self):
        return f'{self.alarm_class}: {", ".join(self.labels)}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


@bi_sync
class AlarmGroup(Document):
    meta = {
        "collection": "alarmgroups",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["reference_prefix", ("rules.alarm_class", "rules.labels")],
    }

    name = StringField(unique=True)
    description = StringField()
    is_active = BooleanField(default=True)
    #
    rules = ListField(EmbeddedDocumentField(MatchRule))
    #
    group_reference = StringField(default="")
    # Group Alarm Class (Group by default)
    group_alarm_class = PlainReferenceField(AlarmClass)
    # Group Title template
    group_title_template = StringField()
    #
    handler = PlainReferenceField(Handler)
    notification_group = ForeignKeyField(NotificationGroup, required=False)
    # BI ID
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_AC_NAME = "Group"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> "AlarmGroup":
        return AlarmGroup.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> "AlarmGroup":
        return AlarmGroup.objects.filter(bi_id=id).first()

    @classmethod
    def get_effective_group(cls, reference_prefix: str, labels: List[str] = None) -> "AlarmGroup":
        return (
            AlarmGroup.objects.filter(reference_prefix=reference_prefix, labels__in=[labels])
            .order_by("preference")
            .first()
        )
