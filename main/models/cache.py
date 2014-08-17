## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cache collection
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.core.cache.backends.db import BaseDatabaseCache
## NOC modules
from noc.lib.nosql import (Document, StringField,
                           BinaryField, DateTimeField)


class Cache(Document):
    meta = {
        "collection": "noc.cache",
        "allow_inheritance": False
    }
    key = StringField(db_field="_id", primary_key=True)
    value = BinaryField(db_field="v")
    pickled_value = BinaryField(db_field="p")
    expires = DateTimeField(db_field="e")

    def __unicode__(self):
        return unicode(self.key)


## @todo: MongoEngine 0.7.x and later allows to specify ttl index
## directly in the meta's indexes
Cache._get_collection().ensure_index(
    "e",
    expireAfterSeconds=0
)
