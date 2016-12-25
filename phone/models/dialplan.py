# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DialPlan model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField
import cachetools

id_lock = Lock()


class DialPlan(Document):
    meta = {
        "collection": "noc.dialplans"
    }

    name = StringField(unique=True)
    description = StringField()
    # Phone mask (regular expression)
    mask = StringField()

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return DialPlan.objects.filter(id=id).first()

    def get_category(self, number):
        """
        Returns number category for a number
        :param number:
        :return:
        """
        from numbercategory import NumberCategory

        for dialplan, rx, category in NumberCategory.get_rules():
            if dialplan != self:
                continue
            if rx.search(number):
                return category
        return None
