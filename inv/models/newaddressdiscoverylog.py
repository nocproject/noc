# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NewAddressDiscoveryLog model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField


@six.python_2_unicode_compatible
class NewAddressDiscoveryLog(Document):
    meta = {
        "collection": "noc.log.discovery.address.new",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["-timestamp"]
    }
    timestamp = DateTimeField()
    vrf = StringField()
    address = StringField()
    description = StringField()
    managed_object = StringField()
    interface = StringField()

    def __str__(self):
        return "%s new %s:%s" % (self.timestamp, self.vrf, self.address)
