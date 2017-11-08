# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MRTConfig
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.lib.nosql import Document, StringField, BooleanField, \
    IntField, ForeignKeyField
# NOC modules
from noc.main.models import PyRule
from noc.sa.models.managedobjectselector import ManagedObjectSelector


class MRTConfig(Document):
    meta = {
        "collection": "noc.mrtconfig",
        "strict": False,
        "auto_create_index": False
    }
    name = StringField(unique=True)
    is_active = BooleanField(default=True)
    description = StringField(required=False)
    permission_name = StringField(required=True)
    selector = ForeignKeyField(ManagedObjectSelector, required=True)
    reduce_pyrule = ForeignKeyField(PyRule, required=True)
    map_script = StringField(required=True)
    timeout = IntField(required=False)

    def __unicode__(self):
        return self.name
