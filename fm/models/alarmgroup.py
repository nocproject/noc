# ---------------------------------------------------------------------
# AlarmGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
import uuid

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, IntField, ListField, LongField
import cachetools

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from .alarmclass import AlarmClass


id_lock = Lock()


@bi_sync
class AlarmGroup(Document):
    meta = {
        "collection": "alarmgroups",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["reference_prefix", ("reference_prefix", "labels")],
    }

    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField()
    preference = IntField(default=999)
    reference_prefix = StringField()
    labels = ListField(StringField())
    # Group Alarm Class (Group by default)
    alarm_class = PlainReferenceField(AlarmClass)
    # Group Title template
    title_template = StringField()
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
