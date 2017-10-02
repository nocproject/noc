# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Building object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, BooleanField,
                                ListField, EmbeddedDocumentField,
                                DictField, DateTimeField)
# NOC modules
from noc.lib.nosql import PlainReferenceField
from .entrance import Entrance
from .division import Division
from noc.core.model.decorator import on_save


@on_save
class Building(Document):
    meta = {
        "collection": "noc.buildings",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["adm_division", "data", "sort_order"]
    }
    # Administrative division
    adm_division = PlainReferenceField(Division)

    status = StringField(
        choices=[
            ("P", "PROJECT"),
            ("B", "BUILDING"),
            ("R", "READY"),
            ("E", "EVICTED"),
            ("D", "DEMOLISHED")
        ],
        default="R")
    # Total homes
    homes = IntField()
    # Maximal amount of floors
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
    # Internal field for sorting
    # Filled by primary address trigger
    sort_order = StringField()

    @property
    def primary_address(self):
        from .address import Address

        # Try primary address first
        pa = Address.objects.filter(building=self.id, is_primary=True).first()
        if pa:
            return pa
        # Fallback to first address found
        return Address.objects.filter(building=self.id).first()

    def fill_entrances(self, first_entrance=1, first_home=1,
                       n_entrances=1, first_floor=1, last_floor=1,
                       homes_per_entrance=1):
        e_home = first_home
        for e in range(first_entrance, first_entrance + n_entrances):
            self.entrances += [
                Entrance(
                    number=str(e),
                    first_floor=str(first_floor),
                    last_floor=str(last_floor),
                    first_home=str(e_home),
                    last_home=str(e_home + homes_per_entrance - 1)
                )
            ]
            e_home += homes_per_entrance
        self.save()
