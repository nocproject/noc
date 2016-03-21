# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Pool model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField


class Pool(Document):
    meta = {
        "collection": "noc.pools"
    }

    name = StringField(unique=True, min_length=1, max_length=16,
                       regex="^[0-9a-zA-Z]{1,16}$")
    description = StringField()

    _name_cache = {}

    def __unicode__(self):
        return self.name

    @classmethod
    def get_name_by_id(cls, id):
        id = str(id)
        if id not in cls._name_cache:
            try:
                cls._name_cache[id] = Pool.objects.get(id=id).name
            except Pool.DoesNotExist:
                cls._name_cache[id] = None
        return cls._name_cache[id]
