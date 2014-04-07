# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Building object
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, BooleanField,
                                ListField, EmbeddedDocumentField,
                                DictField, DateTimeField)
from mongoengine import signals
## NOC modules
from noc.lib.nosql import PlainReferenceField
from entrance import Entrance
from division import Division


class Building(Document):
    meta = {
        "collection": "noc.buildings",
        "allow_inheritance": False,
        "indexes": ["adm_division", "data"]
    }
    # Administrative division
    adm_division = PlainReferenceField(Division)

    status = StringField(choices=[
        ("P", "PROJECT"),
        ("B", "BUILDING"),
        ("R", "READY"),
        ("E", "EVICTED"),
        ("D", "DEMOLISHED")
    ])
    ## Total homes
    homes = IntField()
    ## Maximal amount of floors
    floors = IntField()
    #
    entrances = ListField(EmbeddedDocumentField(Entrance))
    #
    has_cellar = BooleanField()
    has_attic = BooleanField()
    #
    postal_code = StringField()
    # Type
    is_administrative = BooleanField(default=False)
    is_habitated = BooleanField(default=False)
    #
    data = DictField()
    #
    start_date = DateTimeField()
    end_date = DateTimeField()

    @classmethod
    def update_floors(cls, sender, document, **kwargs):
        """
        Update floors
        """

    @property
    def primary_address(self):
        return Address.objects.filter(building=self.id).first()

## Setup signals
signals.pre_save.connect(Building.update_floors, sender=Building)

## Avoid circular references
from address import Address
