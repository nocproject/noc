## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NewPrefixDiscoveryLog model
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField


class NewPrefixDiscoveryLog(Document):
    meta = {
        "collection": "noc.log.discovery.prefix.new",
        "allow_inheritance": False,
        "indexes": ["-timestamp"]
    }
    timestamp = DateTimeField()
    vrf = StringField()
    prefix = StringField()
    description = StringField()
    managed_object = StringField()
    interface = StringField()

    def __unicode__(self):
        return "%s new %s:%s" % (self.timestamp, self.vrf, self.prefix)
