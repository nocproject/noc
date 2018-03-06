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
from mongoengine.document import Document
from mongoengine.fields import StringField
import cachetools
# NOC modules

id_lock = Lock()


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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ThresholdProfile.objects.filter(id=id).first()
