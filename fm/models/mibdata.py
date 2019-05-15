# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MIBData model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import six
# NOC modules
import noc.lib.nosql as nosql
from .mib import MIB


@six.python_2_unicode_compatible
class MIBData(nosql.Document):
    meta = {
        "collection": "noc.mibdata",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["oid", "name", "mib", "aliases"]
    }
    mib = nosql.PlainReferenceField(MIB)
    oid = nosql.StringField(required=True, unique=True)
    name = nosql.StringField(required=True)
    description = nosql.StringField(required=False)
    syntax = nosql.DictField(required=False)
    aliases = nosql.ListField(nosql.StringField(), default=[])

    def __str__(self):
        return self.name
