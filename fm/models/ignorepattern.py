# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IgnorePattern model
# Propagated to collectors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField


@six.python_2_unicode_compatible
class IgnorePattern(Document):
    meta = {"collection": "noc.fm.ignorepatterns", "strict": False, "auto_create_index": False}

    source = StringField()
    pattern = StringField()
    is_active = BooleanField()
    description = StringField(required=False)

    def __str__(self):
        return "%s: %s" % (self.source, self.pattern)
