# ----------------------------------------------------------------------
# SensorProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from threading import Lock
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, LongField, BooleanField
import cachetools

# NOC modules
from noc.main.models.style import Style
from noc.wf.models.workflow import Workflow
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField


id_lock = Lock()


@bi_sync
@on_delete_check(check=[("inv.Sensor", "profile")])
class SensorProfile(Document):
    meta = {"collection": "sensorprofiles", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    workflow = PlainReferenceField(Workflow)
    style = ForeignKeyField(Style)
    enable_collect = BooleanField(default=False)
    tags = ListField(StringField())
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKDLOW_NAME = "Sensor Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> "SensorProfile":
        return SensorProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> "SensorProfile":
        return SensorProfile.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "SensorProfile":
        sp = SensorProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not sp:
            sp = SensorProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKDLOW_NAME).first(),
            )
            sp.save()
        return sp
