# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# PhoneRange model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField, ListField, ObjectIdField
from mongoengine.errors import ValidationError
import cachetools
# NOC modules
from .phonerange import PhoneRange
from .numbercategory import NumberCategory
from noc.sa.models.service import Service
from noc.project.models.project import Project
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.lib.nosql import ForeignKeyField, PlainReferenceField
from noc.lib.text import clean_number
from noc.core.resourcegroup.decorator import resourcegroup
from noc.wf.models.state import State
from noc.core.wf.decorator import workflow
from .dialplan import DialPlan
from .phonenumberprofile import PhoneNumberProfile

id_lock = Lock()


@resourcegroup
@workflow
class PhoneNumber(Document):
    meta = {
        "collection": "noc.phonenumbers",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "static_service_groups",
            "effective_service_groups",
            "static_client_groups",
            "effective_client_groups"
        ]
    }

    number = StringField()
    profile = PlainReferenceField(PhoneNumberProfile)
    state = PlainReferenceField(State)
    dialplan = PlainReferenceField(DialPlan)
    phone_range = PlainReferenceField(PhoneRange)
    category = PlainReferenceField(NumberCategory)
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
    #
    administrative_domain = ForeignKeyField(AdministrativeDomain)
    # Resource groups
    static_service_groups = ListField(ObjectIdField())
    effective_service_groups = ListField(ObjectIdField())
    static_client_groups = ListField(ObjectIdField())
    effective_client_groups = ListField(ObjectIdField())

    _id_cache = cachetools.TTLCache(100, ttl=60)

    def __unicode__(self):
        return self.number

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return PhoneNumber.objects.filter(id=id).first()

    def clean(self):
        super(PhoneNumber, self).clean()
        # Check number is valid integer
        self.number = clean_number(self.number or "")
        if not self.number:
            raise ValidationError("Empty phone number")
        # Change parent
        self.phone_range = PhoneRange.get_closest_range(
            dialplan=self.dialplan,
            from_number=self.number
        )
        # Set profile when necessary
        if not self.profile:
            self.profile = self.phone_range.profile.default_number_profile

    @property
    def enum(self):
        return ".".join(reversed(self.number)) + ".e164.arpa"
