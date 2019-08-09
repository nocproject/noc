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
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, ListField
import six

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .mib import MIB


@six.python_2_unicode_compatible
class MIBData(Document):
    meta = {
        "collection": "noc.mibdata",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["oid", "name", "mib", "aliases"],
    }
    mib = PlainReferenceField(MIB)
    oid = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField(required=False)
    syntax = DictField(required=False)
    aliases = ListField(StringField(), default=[])

    def __str__(self):
        return self.name
