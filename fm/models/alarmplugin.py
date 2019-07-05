# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmPlugin model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine import fields
from mongoengine.document import EmbeddedDocument


@six.python_2_unicode_compatible
class AlarmPlugin(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    name = fields.StringField()
    config = fields.DictField(default={})

    def __str__(self):
        return self.name
