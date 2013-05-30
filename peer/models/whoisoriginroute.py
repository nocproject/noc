# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## WhoisOriginRoute model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib import nosql


class WhoisOriginRoute(nosql.Document):
    """
    origin -> route
    """
    meta = {
        "collection": "noc.whois.origin.route",
        "allow_inheritance": False
    }

    origin = nosql.StringField(unique=True)
    routes = nosql.ListField(nosql.StringField())

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
        c.insert(data, manipulate=False, check_keys=False)
        # Reindex
        c.ensure_index("origin")
        return c.count()
