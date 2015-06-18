## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NewAddressDiscoveryLog model
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField


class NewAddressDiscoveryLog(Document):
    meta = {
        "collection": "noc.log.discovery.address.new",
        "allow_inheritance": False,
        "indexes": ["-timestamp"]
    }
    timestamp = DateTimeField()
    vrf = StringField()
    address = StringField()
    description = StringField()
    managed_object = StringField()
    interface = StringField()

    def __unicode__(self):
        return "%s new %s:%s" % (self.timestamp, self.vrf, self.address)
