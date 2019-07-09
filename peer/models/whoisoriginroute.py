# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# WhoisOriginRoute model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, ListField


@six.python_2_unicode_compatible
class WhoisOriginRoute(Document):
    """
    origin -> route
    """

    meta = {"collection": "noc.whois.origin.route", "strict": False, "auto_create_index": False}

    origin = StringField(primary_key=True)
    routes = ListField(StringField())

    def __str__(self):
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
        c.insert(
            [{"_id": k.upper(), "routes": data[k]} for k in data],
            manipulate=False,
            check_keys=False,
        )
        # Implicit reindex
        return cls.objects.count()
