# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Subscriber
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, ReferenceField, ListField
## NOC modules
from subscriberprofile import SubscriberProfile


class Subscriber(Document):
    meta = {
        "collection": "noc.subscribers"
    }

    name = StringField()
    description = StringField()
    profile = ReferenceField(SubscriberProfile)
    tags = ListField(StringField())

    def __unicode__(self):
        return self.name
