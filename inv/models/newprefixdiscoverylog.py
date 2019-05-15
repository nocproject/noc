# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NewPrefixDiscoveryLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField


@six.python_2_unicode_compatible
class NewPrefixDiscoveryLog(Document):
    meta = {
        "collection": "noc.log.discovery.prefix.new",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["-timestamp"]
    }
    timestamp = DateTimeField()
    vrf = StringField()
    prefix = StringField()
    description = StringField()
    managed_object = StringField()
    interface = StringField()

    def __str__(self):
        return "%s new %s:%s" % (self.timestamp, self.vrf, self.prefix)
