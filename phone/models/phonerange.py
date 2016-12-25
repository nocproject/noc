# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PhoneRange model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from threading import Lock
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField
from mongoengine.queryset import Q
from mongoengine.errors import ValidationError
import cachetools
## NOC modules
from dialplan import DialPlan
from phonerangeprofile import PhoneRangeProfile
from noc.lib.nosql import PlainReferenceField
from noc.crm.models.supplier import Supplier
from noc.project.models.project import Project
from noc.lib.nosql import ForeignKeyField

id_lock = Lock()


class PhoneRange(Document):
    meta = {
        "collection": "noc.phoneranges"
    }

    name = StringField()
    description = StringField()
    profile = PlainReferenceField(PhoneRangeProfile)
    dialplan = PlainReferenceField(DialPlan)
    parent = PlainReferenceField("self")
    from_number = StringField()
    to_number = StringField()
    supplier = PlainReferenceField(Supplier)
    project = ForeignKeyField(Project)
    # @todo: softswitch
    # @todo: SBC
    # @todo: tags

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return PhoneRange.objects.filter(id=id).first()

    @classmethod
    def get_closest_range(cls, dialplan, from_number,
                          to_number=None, exclude_range=None):
        """
        Find closest range enclosing given range
        :param dialplan:
        :param from_number:
        :param to_number:
        :param exclude_range:
        :return: Phone range or None
        """
        to_number = to_number or from_number
        if to_number < from_number:
            from_number, to_number = to_number, from_number
        q = {
            "dialplan": dialplan.id,
            "from_number__lte": from_number,
            "to_number__gte": to_number
        }
        if exclude_range:
            q["id__ne"] = exclude_range.id
        return PhoneRange.objects.filter(**q)\
            .order_by("from_number", "-to_number").first()

    def clean(self):
        if self.to_number < self.from_number:
            self.from_number, self.to_number = self.to_number, self.from_number
        super(PhoneRange, self).clean()
        # Check overlapped ranges
        q = Q(dialplan=self.dialplan.id) & (
            Q(
                from_number__gt=self.from_number,
                from_number__lte=self.to_number,
                to_number__gte=self.to_number
            ) | Q(
                to_number__lt=self.to_number,
                from_number__lte=self.from_number,
                to_number__gte=self.from_number
            ) | Q(
                from_number=self.from_number,
                to_number=self.to_number
            )
        )
        if self.id:
            q &= Q(id__ne=self.id)
        rr = PhoneRange.objects.filter(q).first()
        if rr:
            raise ValidationError("Overlapped ranges: %s - %s" % (rr.from_number, rr.to_number))
        q = {
            "dialplan": self.dialplan,
            "from_number": self.from_number,
            "to_number": self.to_number
        }
        if self.id:
            q["exclude_range"] = self
        self.parent = PhoneRange.get_closest_range(**q)

    @property
    def total_numbers(self):
        """
        Total phone numbers in range
        """
        return int(self.to_number) - int(self.from_number) + 1
