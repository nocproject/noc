# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MIBData model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
import noc.lib.nosql as nosql
from mib import MIB


class MIBData(nosql.Document):
    meta = {
        "collection": "noc.mibdata",
        "strict": False,
        "indexes": ["oid", "name", "mib", "aliases"]
    }
    mib = nosql.PlainReferenceField(MIB)
    oid = nosql.StringField(required=True, unique=True)
    name = nosql.StringField(required=True)
    description = nosql.StringField(required=False)
    syntax = nosql.DictField(required=False)
    aliases = nosql.ListField(nosql.StringField(), default=[])

    def __unicode__(self):
        return self.name
