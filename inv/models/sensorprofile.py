# ----------------------------------------------------------------------
# SensorProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from threading import Lock
from typing import Optional, Union
import operator
from functools import partial

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    LongField,
    BooleanField,
    EmbeddedDocumentField,
    IntField,
)
import cachetools

# NOC modules
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.pm.models.measurementunits import MeasurementUnits
from noc.wf.models.workflow import Workflow
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField


id_lock = Lock()


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0)
    labels = ListField(StringField())
    handler = StringField()

    def __str__(self):
        return ", ".join(self.labels)


@bi_sync
@Label.model
@on_delete_check(check=[("inv.Sensor", "profile")])
class SensorProfile(Document):
    meta = {
        "collection": "sensorprofiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "labels",
            "match_rules.labels",
            ("dynamic_classification_policy", "match_rules.labels"),
        ],
    }

    name = StringField(unique=True)
    description = StringField()
    workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "inv.SensorProfile")
    )
    style = ForeignKeyField(Style)
    enable_collect = BooleanField(default=False)
    collect_interval = IntField(default=60)
    units = PlainReferenceField(MeasurementUnits)
    # Dynamic Profile Classification
    dynamic_classification_policy = StringField(
        choices=[("R", "By Rule"), ("D", "Disable")],
        default="R",
    )
    #
    match_rules = ListField(EmbeddedDocumentField(MatchRule))
    # Labels
    labels = ListField(StringField())
    # BI ID
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Sensor Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["SensorProfile"]:
        return SensorProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["SensorProfile"]:
        return SensorProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "SensorProfile":
        sp = SensorProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
        if not sp:
            sp = SensorProfile(
                name=cls.DEFAULT_PROFILE_NAME,
                workflow=Workflow.objects.filter(name=cls.DEFAULT_WORKFLOW_NAME).first(),
            )
            sp.save()
        return sp

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_sensorprofile")
