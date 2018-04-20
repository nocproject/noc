# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# WhoisOriginRoute model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# Third-party modules
=======
##----------------------------------------------------------------------
## WhoisOriginRoute model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField


class WhoisOriginRoute(Document):
    """
    origin -> route
    """
    meta = {
        "collection": "noc.whois.origin.route",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
    }

    origin = StringField(primary_key=True)
=======
        "allow_inheritance": False
    }

    origin = StringField(primary_key=True, unique=True)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    routes = ListField(StringField())

    def __unicode__(self):
        return self.as_set

    @classmethod
    def lookup(cls, key):
        v = cls.objects.filter(origin=key.upper()).first()
        if v is None:
            return []
        else:
            return v.routes

    @classmethod
    def upload(cls, data):
        """
        Replace cache with the new data
        :param cls:
        :param data: List of {origin:, routes:}
        :return: Number of inserted records
        """
        c = cls._get_collection()
        c.drop()
        c.insert([{"_id": k.upper(), "routes": data[k]} for k in data],
                 manipulate=False, check_keys=False)
        # Implicit reindex
        return cls.objects.count()
