# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Street object
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, DictField, BooleanField, DateTimeField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_delete_check
from noc.core.comp import smart_text
from .division import Division


@on_delete_check(check=[("gis.Address", "street")])
@six.python_2_unicode_compatible
class Street(Document):
    meta = {
        "collection": "noc.streets",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["parent", "data"],
    }
    #
    parent = PlainReferenceField(Division)
    # Normalized name
    name = StringField()
    # street/town/city, etc
    short_name = StringField()
    #
    is_active = BooleanField(default=True)
    # Additional data
    # Depends on importer
    data = DictField()
    #
    start_date = DateTimeField()
    end_date = DateTimeField()

    def __str__(self):
        if self.short_name:
            return "%s, %s" % (self.name, self.short_name)
        else:
            return self.name

    @property
    def full_path(self):
        if not self.parent:
            return ""
        r = [self.parent.full_path, smart_text(self)]
        return " | ".join(r)
