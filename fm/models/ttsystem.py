# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TTSystem
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField
import cachetools
## NOC modules
from noc.core.handler import get_handler



class TTSystem(Document):
    meta = {
        "collection": "noc.ttsystem",
        "allow_inheritance": False
    }

    name = StringField(unique=True)
    # Full path to BaseTTSystem instance
    handler = StringField()
    description = StringField()
    # Connection string
    connection = StringField()
    #
    tags = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"))
    def get_by_name(cls, name):
        t = TTSystem.objects.filter(name=name).first()
        if t:
            return t.get_system()
        else:
            return None

    def get_system(self):
        """
        Return BaseTTSystem instance
        """
        h = get_handler(self.handler)
        if not h:
            raise ValueError
        return h(self.name, self.connection)
