# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Subscriber Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField, IntField
import cachetools
# NOC models
from noc.lib.nosql import ForeignKeyField, PlainReferenceField
from noc.main.models.style import Style
from noc.wf.models.workflow import Workflow


class SubscriberProfile(Document):
    meta = {
        "collection": "noc.subscriberprofiles",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style, required=False)
    workflow = PlainReferenceField(Workflow)
    # FontAwesome glyph
    glyph = StringField()
    tags = ListField(StringField())
    # Alarm weight
    weight = IntField(default=0)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"))
    def get_by_id(self, id):
        return SubscriberProfile.objects.filter(id=id).first()
