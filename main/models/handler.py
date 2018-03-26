# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Approved handlers
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField
import cachetools

id_lock = Lock()


class Handler(Document):
    meta = {
        "collection": "handlers",
        "strict": False,
        "auto_create_index": False,
    }

    handler = StringField(primary_key=True)
    name = StringField()
    description = StringField()
    allow_config_filter = BooleanField()
    allow_config_validation = BooleanField()

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Handler.objects.filter(handler=id).first()
