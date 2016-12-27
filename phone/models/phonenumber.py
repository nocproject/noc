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
from mongoengine.fields import StringField, DateTimeField
import cachetools
## NOC modules
from phonerange import PhoneRange
from numbercategory import NumberCategory
from noc.sa.models.service import Service
from dialplan import DialPlan
from phonenumberprofile import PhoneNumberProfile
from noc.lib.nosql import PlainReferenceField
from noc.project.models.project import Project
from noc.lib.nosql import ForeignKeyField

id_lock = Lock()


class PhoneNumber(Document):
    meta = {
        "collection": "noc.phonenumbers"
    }

    number = StringField()
    profile = PlainReferenceField(PhoneNumberProfile)
    dialplan = PlainReferenceField(DialPlan)
    phone_range = PlainReferenceField(PhoneRange)
    category = PlainReferenceField(NumberCategory)
    status = StringField(
        default="N",
        choices=[
            ("N", "New"),
            ("F", "Free"),
            ("A", "Allocated"),
            ("R", "Reserved"),
            ("O", "Out-of-order"),
            ("C", "Cooldown")
        ]
    )
    description = StringField()
    service = PlainReferenceField(Service)
    project = ForeignKeyField(Project)
    protocol = StringField(
        default="SIP",
        choices=[
            ("SIP", "SIP"),
            ("H323", "H.323"),
            ("SS7", "SS7"),
            ("MGCP", "MGCP"),
            ("H247", "H.247"),
            ("ISDN", "ISDN"),
            ("Skinny", "Skinny")
        ]
    )
    # Auto-change status to F after *allocated_till*
    allocated_till = DateTimeField()
    # Last state change
    changed = DateTimeField()

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return PhoneRange.objects.filter(id=id).first()

    def clean(self):
        super(PhoneNumber, self).clean()
        # Change parent
        self.phone_range = PhoneRange.get_closest_range(
            dialplan=self.dialplan,
            from_number=self.number
        )
