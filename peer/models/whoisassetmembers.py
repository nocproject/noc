# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## WhoisASSetMembers model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib import nosql


class WhoisASSetMembers(nosql.Document):
    """
    as-set -> members lookup
    """
    meta = {
        "collection": "noc.whois.asset.members",
        "allow_inheritance": False
    }

    as_set = nosql.StringField(unique=True)
    members = nosql.ListField(nosql.StringField())

    def __unicode__(self):
        return self.as_set

    @classmethod
    def lookup(cls, key):
        v = cls.objects.filter(as_set=key.upper()).first()
        if v is None:
            return []
        else:
            return v.members

    @classmethod
    def upload(cls, data):
        """
        Replace cache with the new data
        :param cls:
        :param data: List of {as_set:, members:}
        :return: Number of inserted records
        """
        c = cls._get_collection()
        c.drop()
        c.insert(data, manipulate=False, check_keys=False)
        # Reindex
        c.ensure_index("as_set")
        return c.count()
