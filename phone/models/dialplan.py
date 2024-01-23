# ---------------------------------------------------------------------
# DialPlan model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(check=[("phone.PhoneRange", "dialplan"), ("phone.PhoneNumber", "dialplan")])
class DialPlan(Document):
    meta = {"collection": "noc.dialplans", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    # Phone mask (regular expression)
    mask = StringField()

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["DialPlan"]:
        return DialPlan.objects.filter(id=oid).first()

    def get_category(self, number):
        """
        Returns number category for a number
        :param number:
        :return:
        """
        from .numbercategory import NumberCategory

        for dialplan, rx, category in NumberCategory.get_rules():
            if dialplan != self:
                continue
            if rx.search(number):
                return category
        return None
