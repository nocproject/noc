# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PhoneLinkType model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, IntField,
                                ListField, EmbeddedDocumentField)
import cachetools
# NOC modules
from dialplan import DialPlan
from noc.lib.nosql import PlainReferenceField

id_lock = Lock()


class PhoneLinkType(Document):
    meta = {
        "collection": "noc.phonelinktypes"
    }

    name = StringField(unique=True)
    is_active = BooleanField()
    code = StringField(unique=True)
    description = StringField()

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return PhoneLinkType.objects.filter(id=id).first()
