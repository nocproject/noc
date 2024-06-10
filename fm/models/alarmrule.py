# ---------------------------------------------------------------------
# AlarmRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, List, Union

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    LongField,
    IntField,
    ReferenceField,
    EmbeddedDocumentField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.label import Label
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.core.bi.decorator import bi_sync
from .alarmseverity import AlarmSeverity
from .alarmclass import AlarmClass
from .escalationprofile import EscalationProfile


id_lock = Lock()


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    alarm_class: AlarmClass = ReferenceField(AlarmClass)
    severity: AlarmSeverity = ReferenceField(AlarmSeverity, required=False)
    reference_rx = StringField()

    def __str__(self):
        return f'{", ".join(self.labels)}, {self.alarm_class or ""}/{self.reference_rx}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


class Group(EmbeddedDocument):
    # Group Alarm reference Template
    reference_template = StringField(default="")
    # Group Alarm Class (Group by default)
    alarm_class = PlainReferenceField(AlarmClass)
    # Group Title template
    title_template = StringField(default="")
    # Minimum amount of alarms to create the group
    min_threshold = IntField(default=0, min_value=0)
    # Maximum amount of alarms to create the group
    max_threshold = IntField(default=1, min_value=0)
    # Correlation window in seconds to check min_threshold
    window = IntField(default=0, min_value=0)
    # Labels for set Group Alarm
    labels = ListField(StringField())

    def __str__(self):
        return f'{self.alarm_class or ""}/{self.title_template or ""}: {self.reference_template}'


class Action(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    when = StringField(
        default="raise",
        choices=[
            ("raise", "When raise alarm"),
            ("clear", "When clear alarm"),
        ],
    )
    policy = StringField(
        default="continue",
        choices=[
            ("continue", "Continue processed"),
            ("drop", "Drop Alarm"),
            ("rewrite", "Rewrite Alarm Class"),
        ],
    )
    handler = PlainReferenceField(Handler)
    notification_group = ForeignKeyField(NotificationGroup, required=False)
    severity_action = StringField(choices=["set", "min", "max", "inc", "dec"])
    severity: AlarmSeverity = ReferenceField(AlarmSeverity)
    escalation: EscalationProfile = ReferenceField(EscalationProfile)
    # Sync collection Default ?
    alarm_class = PlainReferenceField(AlarmClass)

    def __str__(self):
        return f"{self.when}: {self.policy}"


@bi_sync
class AlarmRule(Document):
    meta = {
        "collection": "alarmrules",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["match.labels", ("match.alarm_class", "match.labels")],
    }

    name = StringField(unique=True)
    description = StringField()
    is_active = BooleanField(default=True)
    #
    match: List[Match] = ListField(EmbeddedDocumentField(Match))
    #
    groups: List[Group] = ListField(EmbeddedDocumentField(Group))
    #
    actions: List[Action] = ListField(EmbeddedDocumentField(Action))
    #
    severity_policy = StringField(
        choices=[
            ("CB", "Class Based Policy"),
            ("AB", "Affected Based Severity Preferred"),
            ("AL", "Affected Limit"),
            ("ST", "By Tokens"),
        ],
        default="AL",
    )
    stop_processing = BooleanField(default=False)
    # BI ID
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_AC_NAME = "Group"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["AlarmRule"]:
        return AlarmRule.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["AlarmRule"]:
        return AlarmRule.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["AlarmRule"]:
        return AlarmRule.objects.filter(bi_id=bi_id).first()
