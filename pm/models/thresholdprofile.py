# ----------------------------------------------------------------------
# ThresholdProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    IntField,
    UUIDField,
    ListField,
    EmbeddedDocumentField,
    FloatField,
)
import cachetools

# NOC modules
from noc.main.models.template import Template
from noc.main.models.handler import Handler
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.eventclass import EventClass
from noc.core.model.decorator import on_delete_check
from noc.core.window import wf_choices
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.window import get_window_function
from noc.core.prettyjson import to_json


id_lock = Lock()


class ThresholdConfig(EmbeddedDocument):
    # Open condition
    op = StringField(choices=["<", "<=", ">=", ">"])
    value = FloatField()
    # Closing condition
    clear_op = StringField(choices=["<", "<=", ">=", ">"])
    clear_value = FloatField()
    # Umbrella alarm class
    alarm_class = PlainReferenceField(AlarmClass)
    # Send event to correlator
    open_event_class = PlainReferenceField(EventClass)
    close_event_class = PlainReferenceField(EventClass)
    # Handlers to call on open and close thresholds
    open_handler = PlainReferenceField(Handler)
    close_handler = PlainReferenceField(Handler)
    #
    template = ForeignKeyField(Template)

    def __str__(self):
        return "%s %s %s %s" % (self.op, self.value, self.clear_op, self.clear_value)

    def is_open_match(self, value):
        """
        Check if threshold profile is matched for open condition
        :param value:
        :return:
        """
        return (
            (self.op == "<" and value < self.value)
            or (self.op == "<=" and value <= self.value)
            or (self.op == ">=" and value >= self.value)
            or (self.op == ">" and value > self.value)
        )

    def is_clear_match(self, value):
        """
        Check if threshold profile is matched for clear condition
        :param value:
        :return:
        """
        return (
            (self.clear_op == "<" and value < self.clear_value)
            or (self.clear_op == "<=" and value <= self.clear_value)
            or (self.clear_op == ">=" and value >= self.clear_value)
            or (self.clear_op == ">" and value > self.clear_value)
        )

    @property
    def name(self):
        return "%s %s %s %s" % (self.op, self.value, self.clear_op, self.clear_value)

    def to_json(self):
        v = {
            "op": self.op,
            "value": self.value,
            "clear_op": self.clear_op,
            "clear_value": self.clear_value,
        }
        if self.alarm_class:
            v["alarm_class__name"] = str(self.alarm_class.name)
        if self.open_event_class:
            v["open_event_class__name"] = str(self.open_event_class.name)
        if self.close_event_class:
            v["close_event_class__name"] = str(self.close_event_class.name)
        if self.open_handler:
            v["open_handler__name"] = str(self.open_handler.name)
        if self.close_handler:
            v["close_handler__name"] = str(self.close_handler.name)
        if self.template:
            v["template__name"] = str(self.template.name)
        return v


# @todo: on_delete_check for ManagedObjectProfile
@on_delete_check(
    check=[
        ("inv.InterfaceProfile", "metrics__threshold_profile"),
    ]
)
class ThresholdProfile(Document):
    meta = {
        "collection": "thresholdprofiles",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.thresholdprofiles",
        "json_unique_fields": ["uuid", "name"],
    }

    name = StringField(unique=True)
    # Global ID
    uuid = UUIDField(binary=True, unique=True)
    description = StringField()
    # Handler to filter and modify umbrella alarms
    umbrella_filter_handler = PlainReferenceField(Handler)
    # Window function settings
    # Window depth
    window_type = StringField(max_length=1, choices=[("m", "Measurements"), ("t", "Time")])
    # Window size. Depends on window type
    # * m - amount of measurements
    # * t - time in seconds
    window = IntField(default=1)
    # Window function
    # Accepts window as a list of [(timestamp, value)]
    # and window_config
    # and returns float value
    window_function = StringField(choices=wf_choices, default="last")
    # Window function configuration
    window_config = StringField()
    # Window preprocessor
    value_handler = PlainReferenceField(Handler)
    # thresholds config
    thresholds = ListField(EmbeddedDocumentField(ThresholdConfig))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name or str(self.uuid)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ThresholdProfile"]:
        return ThresholdProfile.objects.filter(id=oid).first()

    def get_window_function(self):
        """
        Returns window funciton or None if invalid name given
        :returns: Callable or None
        """
        return get_window_function(self.window_function)

    def find_threshold(self, name):
        """
        Find Threshold Config by name
        :param name: Threshold name
        :return: ThresholdConfig or None
        """
        for cfg in self.thresholds:
            if cfg.name == name:
                return cfg
        return None

    def to_json(self) -> str:
        return to_json(
            {
                "name": self.name,
                "$collection": self._meta["json_collection"],
                "uuid": str(self.uuid),
                "description": self.description,
                "umbrella_filter_handler__handler": self.umbrella_filter_handler.handler,
                "window_type": self.window_type,
                "window": self.window,
                "window_function": self.window_function,
                "window_config": self.window_config,
                "value_handler__handler": self.value_handler.handler,
                "thresholds": [thrh.to_json() for thrh in self.thresholds],
            },
            order=["name", "uuid", "thresholds"],
        )

    def get_json_path(self) -> str:
        return "%s.json" % self.uuid
