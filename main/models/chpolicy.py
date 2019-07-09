# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHPolicy model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, IntField


@six.python_2_unicode_compatible
class CHPolicy(Document):
    meta = {"collection": "chpolicies", "strict": False, "auto_create_index": False}

    table = StringField(unique=True)
    is_active = BooleanField(default=True)
    dry_run = BooleanField(default=True)
    ttl = IntField(default=0)

    def __str__(self):
        return self.table
