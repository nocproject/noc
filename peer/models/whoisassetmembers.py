# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## WhoisASSetMembers model
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField


class WhoisASSetMembers(Document):
    """
    as-set -> members lookup
    """
    meta = {
        "collection": "noc.whois.asset.members",
        "allow_inheritance": False
    }

    as_set = StringField(primary_key=True, unique=True)
    members = ListField(StringField())

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
        :param data: Dict of asset -> [members]
        :return: Number of inserted records
        """
        c = cls._get_collection()
        c.drop()
        c.insert([{"_id": k.upper(), "members": data[k]} for k in data],
                 manipulate=False, check_keys=False)
        # Implicit reindex
        return cls.objects.count()
