# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ThresholdProfile model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, IntField, ListField, EmbeddedDocumentField, FloatField
import cachetools
# NOC modules
from noc.main.models.template import Template
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.eventclass import EventClass
from noc.core.window import wf_choices
from noc.lib.nosql import PlainReferenceField, ForeignKeyField

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
    weight = IntField()
    # Send event to correlator
    open_event_class = PlainReferenceField(EventClass)
    close_event_class = PlainReferenceField(EventClass)
    # Handlers to call on open and close thresholds
    open_handler = StringField()
    close_handler = StringField()
    #
    template = ForeignKeyField(Template)

    def __unicode__(self):
        return "%s %s" % (self.op, self.value)


# @todo: on_delete_check
class ThresholdProfile(Document):
    meta = {
        "collection": "thresholdprofiles",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    description = StringField()
    # Handler to filter and modify umbrella alarms
    umbrella_filter_handler = StringField()
    # Window function settings
    # Window depth
    window_type = StringField(
        max_length=1,
        choices=[
            ("m", "Measurements"),
            ("t", "Time")
        ]
    )
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
    # thresholds config
    thresholds = ListField(EmbeddedDocumentField(ThresholdConfig))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ThresholdProfile.objects.filter(id=id).first()
